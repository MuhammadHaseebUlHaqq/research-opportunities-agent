#!/usr/bin/env python3
"""
Hermes opportunity-scout delivery helper.

Takes a JSON array of *vetted* opportunities (produced by the agent following
SKILL.md), dedupes them against a local CSV ledger, then for each NEW one:
  - appends it to the CSV ledger  (~/.hermes/reports/opportunities.csv)
  - creates a row in Airtable
  - includes it in a single email digest

The agent does the searching + judgment; this script does deterministic I/O only.
Stdlib only (urllib, smtplib, csv) — no pip installs.

Usage:
  python3 deliver.py opportunities.json           # normal run
  python3 deliver.py --dry-run opportunities.json # validate + dedup, NO side effects
  cat opportunities.json | python3 deliver.py -   # read JSON from stdin

Input JSON = array of objects. Required: title, url. Optional (with defaults):
  {
    "title": "...",                      # required
    "url": "https://...",                # required — primary dedup key
    "type": "Master's|PhD|Job",          # default Master's
    "university": "...",
    "country": "...",
    "professor": "...",
    "why_fits": "...",
    "funding": "Fully funded|Partial|Unclear",   # default Unclear
    "confidence": "High|Medium|Low"              # default Medium
  }

Env (from ~/.hermes/.env): AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE,
DIGEST_SMTP_USER, DIGEST_SMTP_APP_PASSWORD, DIGEST_EMAIL_TO.
"""
import sys, os, json, csv, re, ssl, smtplib, datetime
import urllib.request, urllib.error, urllib.parse
from email.mime.text import MIMEText

HOME = os.path.expanduser("~/.hermes")
REPORTS = os.path.join(HOME, "reports")
CSV_PATH = os.path.join(REPORTS, "opportunities.csv")

CSV_FIELDS = ["dedup_key", "date_found", "type", "title", "university", "country",
              "professor", "funding", "confidence", "url", "why_fits", "status"]

AIRTABLE_FIELD_MAP = {
    "title": "Title / Role", "type": "Type", "university": "University / Org",
    "country": "Country", "professor": "Professor / Lab", "why_fits": "Why it fits",
    "funding": "Funding", "url": "Source URL", "confidence": "Confidence",
    "date_found": "Date found", "status": "Status",
}
VALID_TYPE = {"Master's", "PhD", "Job"}
VALID_FUNDING = {"Fully funded", "Partial", "Unclear"}
VALID_CONF = {"High", "Medium", "Low"}
ENV_PATH = os.path.join(HOME, ".env")


def load_env():
    """Load ~/.hermes/.env into os.environ (values already set win).

    Parses like python-dotenv, NOT like bash `source`: an unquoted value with
    spaces (e.g. a Gmail app password pasted as 4x4) is kept whole, not split.
    """
    if not os.path.exists(ENV_PATH):
        return
    for line in open(ENV_PATH, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in ("'", '"'):
            val = val[1:-1]
        os.environ.setdefault(key, val)


def norm_key(o):
    url = (o.get("url") or "").strip().lower()
    url = re.sub(r"[?#].*$", "", url).rstrip("/")
    if url:
        return url
    return (o.get("title", "").strip().lower() + "|" +
            o.get("university", "").strip().lower())


def load_seen():
    seen = set()
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                k = row.get("dedup_key", "")
                if k:
                    seen.add(k)
    return seen


def clean(o):
    o = dict(o)
    o["title"] = (o.get("title") or "").strip()
    o["type"] = o.get("type") if o.get("type") in VALID_TYPE else "Master's"
    o["funding"] = o.get("funding") if o.get("funding") in VALID_FUNDING else "Unclear"
    o["confidence"] = o.get("confidence") if o.get("confidence") in VALID_CONF else "Medium"
    for k in ("university", "country", "professor", "why_fits", "url"):
        o[k] = (o.get(k) or "").strip()
    return o


def airtable_post(o):
    tok = os.environ.get("AIRTABLE_API_KEY", "")
    base = os.environ.get("AIRTABLE_BASE_ID", "")
    table = os.environ.get("AIRTABLE_TABLE", "Opportunities")
    if not tok or not base:
        return False, "Airtable env not set"
    fields = {}
    for jk, ak in AIRTABLE_FIELD_MAP.items():
        v = o.get(jk)
        if v:
            fields[ak] = v
    url = f"https://api.airtable.com/v0/{base}/{urllib.parse.quote(table)}"
    data = json.dumps({"fields": fields, "typecast": True}).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {tok}")
    req.add_header("Content-Type", "application/json")
    try:
        urllib.request.urlopen(req, timeout=30)
        return True, ""
    except urllib.error.HTTPError as e:
        return False, f"{e.code}: {e.read().decode()[:200]}"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def send_email(new_items):
    user = os.environ.get("DIGEST_SMTP_USER", "")
    # Gmail app passwords are 16 letters, never spaces — strip any pasted spaces.
    pw = os.environ.get("DIGEST_SMTP_APP_PASSWORD", "").replace(" ", "")
    to = os.environ.get("DIGEST_EMAIL_TO", "") or user
    if not user or not pw:
        return False, "email env not set"
    lines = [f"{len(new_items)} new research opportunity(ies) found by Hermes:\n"]
    for i, o in enumerate(new_items, 1):
        lines.append(f"{i}. [{o['type']}] {o['title']}")
        loc = " — ".join(x for x in (o.get("university"), o.get("country")) if x)
        if loc:
            lines.append(f"   {loc}")
        if o.get("professor"):
            lines.append(f"   Lab/Prof: {o['professor']}")
        lines.append(f"   Funding: {o['funding']}  |  Confidence: {o['confidence']}")
        if o.get("why_fits"):
            lines.append(f"   Why it fits: {o['why_fits']}")
        if o.get("url"):
            lines.append(f"   {o['url']}")
        lines.append("")
    lines.append("Full records (sortable, with status tracking) are in your Airtable base.")
    lines.append("— Hermes · opportunity-scout")
    msg = MIMEText("\n".join(lines))
    msg["Subject"] = f"\U0001F393 {len(new_items)} new research opportunity(ies)"
    msg["From"] = user
    msg["To"] = to
    try:
        # Port 587 STARTTLS — this VPS (Hetzner) blocks 465/25.
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as s:
            s.starttls(context=ssl.create_default_context())
            s.login(user, pw)
            s.sendmail(user, [to], msg.as_string())
        return True, ""
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def main():
    load_env()
    argv = sys.argv[1:]
    dry = "--dry-run" in argv
    argv = [a for a in argv if a != "--dry-run"]
    src = argv[0] if argv else "-"

    raw = sys.stdin.read() if src == "-" else open(src, encoding="utf-8").read()
    try:
        items = json.loads(raw)
    except Exception as e:
        print(f"ERROR: input is not valid JSON: {e}")
        sys.exit(1)
    if isinstance(items, dict):
        items = [items]
    items = [clean(o) for o in items if (o.get("title") and o.get("url"))]

    os.makedirs(REPORTS, exist_ok=True)
    seen = load_seen()
    today = datetime.date.today().isoformat()

    new = []
    for o in items:
        k = norm_key(o)
        if k in seen:
            continue
        seen.add(k)
        o["dedup_key"] = k
        o["date_found"] = today
        o["status"] = "New"
        new.append(o)

    print(f"input={len(items)} valid, new={len(new)}  (ledger: {CSV_PATH})")

    if dry:
        for o in new:
            print(f"  NEW: [{o['type']}] {o['title']}  <{o.get('url')}>")
        print("dry-run: no CSV write, no Airtable, no email.")
        return

    if new:
        newfile = not os.path.exists(CSV_PATH)
        with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
            if newfile:
                w.writeheader()
            for o in new:
                w.writerow(o)

    at_ok = at_fail = 0
    for o in new:
        ok, err = airtable_post(o)
        if ok:
            at_ok += 1
        else:
            at_fail += 1
            print(f"  Airtable FAIL [{o['title'][:40]}]: {err}")
    print(f"Airtable: {at_ok} added, {at_fail} failed")

    if new:
        ok, err = send_email(new)
        print("Email: digest sent" if ok else f"Email FAILED: {err}")
    else:
        print("No new opportunities — nothing added, no email sent.")


if __name__ == "__main__":
    main()
