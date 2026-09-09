#!/usr/bin/env python3
"""Check every http(s) link in a Markdown file and report the ones that fail.

Usage:
    check_links.py README.md [--ignore .linkcheck-ignore] [--output dead-links.json]

A link passes when a GET request, following redirects, ends in a 2xx status.
Each link gets a few attempts with a short pause between them so a brief
hiccup does not count as a failure.

Responses of 403, 429, and 503 usually mean a bot-protection layer refused the
request, not that the page is gone, so they are reported as "blocked" rather
than dead unless --strict is given. The exit code is always 0; the JSON report
is the result.
"""

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlsplit

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/128.0.0.0 Safari/537.36 awesome-wardogs-link-check"
)
ATTEMPTS = 3
PAUSE_SECONDS = (5, 20)
TIMEOUT_SECONDS = 25
WORKERS = 6
MAX_REDIRECTS = 10
BLOCKED_STATUSES = {403, 429, 503}

# Matches http(s) URLs and allows one level of balanced parentheses so that
# links such as https://en.wikipedia.org/wiki/Wardogs_(video_game) survive.
URL_PATTERN = re.compile(r"https?://(?:[^\s()<>\[\]\"']|\([^\s()]*\))+")
TRAILING_PUNCTUATION = ".,;:!?"


def extract_urls(text):
    seen = []
    for match in URL_PATTERN.finditer(text):
        url = match.group(0).rstrip(TRAILING_PUNCTUATION)
        if url not in seen:
            seen.append(url)
    return seen


def load_ignore(path):
    if not path:
        return []
    entries = []
    try:
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line and not line.startswith("#"):
                    entries.append(line)
    except FileNotFoundError:
        pass
    return entries


def is_ignored(url, ignore_entries):
    host = urlsplit(url).hostname or ""
    for entry in ignore_entries:
        if entry.startswith("http://") or entry.startswith("https://"):
            if url.rstrip("/") == entry.rstrip("/"):
                return True
        else:
            domain = entry.lower().lstrip(".")
            if host == domain or host.endswith("." + domain):
                return True
    return False


def fetch_once(url):
    """Return (state, reason) where state is "ok", "blocked", or "dead"."""
    current = url
    for _ in range(MAX_REDIRECTS):
        request = urllib.request.Request(
            current,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                status = response.getcode()
        except urllib.error.HTTPError as error:
            status = error.code
            location = error.headers.get("Location")
            # urllib follows most redirects itself but not 308 on older
            # Pythons, so handle any 3xx that slipped through here.
            if 300 <= status < 400 and location:
                current = urllib.parse.urljoin(current, location)
                continue
        except Exception as error:  # noqa: BLE001 - any network failure counts
            return "dead", f"{type(error).__name__}: {error}"

        if 200 <= status < 300:
            return "ok", f"HTTP {status}"
        if status in BLOCKED_STATUSES:
            return "blocked", f"HTTP {status}"
        return "dead", f"HTTP {status}"
    return "dead", f"more than {MAX_REDIRECTS} redirects"


def check_url(url):
    state, reason = "dead", ""
    for attempt in range(ATTEMPTS):
        state, reason = fetch_once(url)
        if state == "ok":
            break
        if attempt < ATTEMPTS - 1:
            time.sleep(PAUSE_SECONDS[min(attempt, len(PAUSE_SECONDS) - 1)])
    return {"url": url, "state": state, "reason": reason}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("markdown", help="Markdown file to scan")
    parser.add_argument("--ignore", default=None, help="Ignore list path")
    parser.add_argument("--output", default="dead-links.json", help="JSON report path")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat 403, 429, and 503 responses as dead instead of blocked",
    )
    args = parser.parse_args()

    with open(args.markdown, encoding="utf-8") as handle:
        text = handle.read()

    ignore_entries = load_ignore(args.ignore)
    urls = extract_urls(text)
    to_check = [url for url in urls if not is_ignored(url, ignore_entries)]
    skipped = [url for url in urls if url not in to_check]

    print(f"Found {len(urls)} links, checking {len(to_check)}, skipping {len(skipped)}.")

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        results = list(pool.map(check_url, to_check))

    if args.strict:
        for result in results:
            if result["state"] == "blocked":
                result["state"] = "dead"

    dead = [r for r in results if r["state"] == "dead"]
    blocked = [r for r in results if r["state"] == "blocked"]
    markers = {"ok": "ok     ", "blocked": "BLOCKED", "dead": "DEAD   "}
    for result in results:
        print(f"{markers[result['state']]} {result['url']}  ({result['reason']})")

    report = {
        "source": args.markdown,
        "checked": len(to_check),
        "skipped": skipped,
        "blocked": blocked,
        "dead": dead,
    }
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)

    print(f"\n{len(dead)} dead, {len(blocked)} blocked. Report written to {args.output}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
