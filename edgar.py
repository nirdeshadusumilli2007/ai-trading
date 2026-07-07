"""SEC EDGAR Form 4 helper for the public-disclosure trading agent.

Finds fresh open-market insider BUYS (transaction code "P") by officers,
directors, and 10% owners from the EDGAR "current events" Form 4 feed.
Everything here is public data published by the SEC.

Usage (matches PROMPT.md step 2A):

    python -c "import edgar, json; print(json.dumps([edgar.to_dict(b) for b in edgar.fetch_new_insider_buys()]))"

or directly:

    python edgar.py [--min-value 100000] [--limit 100] [--include-seen]

The SEC requires a descriptive User-Agent with contact info on automated
requests. Set EDGAR_USER_AGENT to "Your Name you@example.com" before running.

Stdlib only — no third-party dependencies. Filings already reported in a
previous run are remembered in data/edgar_seen.json and skipped, so each run
returns only new buys.
"""

import dataclasses
import json
import os
import re
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

ATOM_URL = (
    "https://www.sec.gov/cgi-bin/browse-edgar"
    "?action=getcurrent&type=4&company=&dateb=&owner=include&count=100&output=atom"
)
ATOM_NS = {"a": "http://www.w3.org/2005/Atom"}
USER_AGENT = os.environ.get("EDGAR_USER_AGENT", "ai-trading-agent contact@example.com")

DATA_DIR = Path(__file__).resolve().parent / "data"
SEEN_FILE = DATA_DIR / "edgar_seen.json"
SEEN_KEEP = 5000  # accession numbers to remember

_REQUEST_GAP_SECONDS = 0.15  # stay well under the SEC's 10 req/s fair-access limit
_last_request_at = 0.0


@dataclass
class InsiderBuy:
    ticker: str
    issuer_name: str
    insider_name: str
    insider_title: str
    is_officer: bool
    is_director: bool
    is_ten_percent_owner: bool
    transaction_dates: List[str]
    total_shares: float
    avg_price: float
    total_value: float
    shares_owned_after: Optional[float]
    pre_planned_10b5_1: bool
    footnotes: List[str] = field(default_factory=list)
    filed_at: str = ""
    accession_no: str = ""
    filing_url: str = ""


def to_dict(buy: InsiderBuy) -> dict:
    return dataclasses.asdict(buy)


def _get(url: str, timeout: int = 30, retries: int = 3) -> bytes:
    global _last_request_at
    for attempt in range(retries):
        wait = _REQUEST_GAP_SECONDS - (time.monotonic() - _last_request_at)
        if wait > 0:
            time.sleep(wait)
        req = urllib.request.Request(url, headers={
            "User-Agent": USER_AGENT,
            "Accept-Encoding": "identity",
            "Host": "www.sec.gov",
        })
        _last_request_at = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as err:
            if err.code in (429, 503) and attempt < retries - 1:
                time.sleep(2 ** (attempt + 1))
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if attempt < retries - 1:
                time.sleep(2 ** (attempt + 1))
                continue
            raise
    raise RuntimeError(f"unreachable: {url}")


def _load_seen() -> List[str]:
    try:
        return json.loads(SEEN_FILE.read_text())
    except (OSError, ValueError):
        return []


def _save_seen(seen: List[str]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SEEN_FILE.write_text(json.dumps(seen[-SEEN_KEEP:], indent=0) + "\n")


def _text(node: Optional[ET.Element]) -> str:
    return (node.text or "").strip() if node is not None else ""


def _value(parent: Optional[ET.Element], path: str) -> str:
    """Ownership XML wraps most fields as <field><value>x</value></field>."""
    if parent is None:
        return ""
    return _text(parent.find(path + "/value")) or _text(parent.find(path))


def _to_float(raw: str) -> float:
    try:
        return float(raw.replace(",", ""))
    except (ValueError, AttributeError):
        return 0.0


def _is_true(raw: str) -> bool:
    return raw.strip().lower() in ("1", "true")


def _list_filings(max_filings: int) -> List[dict]:
    """Return [{accession, filing_url, filed_at}] for current Form 4 filings
    (amendments 4/A are skipped)."""
    root = ET.fromstring(_get(ATOM_URL))
    filings = []
    for entry in root.findall("a:entry", ATOM_NS):
        category = entry.find("a:category", ATOM_NS)
        if category is not None and category.get("term") != "4":
            continue  # skip 4/A amendments
        link = entry.find("a:link", ATOM_NS)
        href = link.get("href", "") if link is not None else ""
        match = re.search(r"/([\d-]{18,})-index", href)
        if not href or not match:
            continue
        filings.append({
            "accession": match.group(1),
            "filing_url": href,
            "filed_at": _text(entry.find("a:updated", ATOM_NS)),
        })
        if len(filings) >= max_filings:
            break
    return filings


def _find_ownership_xml_url(index_url: str) -> Optional[str]:
    directory = index_url.rsplit("/", 1)[0]
    listing = json.loads(_get(directory + "/index.json"))
    for item in listing.get("directory", {}).get("item", []):
        name = item.get("name", "")
        if name.lower().endswith(".xml"):
            return f"{directory}/{name}"
    return None


def _parse_form4(doc: ET.Element) -> Optional[dict]:
    """Extract aggregate open-market purchase (code P) details, or None."""
    dates, total_shares, total_value, owned_after = [], 0.0, 0.0, None
    for txn in doc.findall(".//nonDerivativeTransaction"):
        if _value(txn, "transactionCoding/transactionCode") != "P":
            continue
        if _value(txn, "transactionAmounts/transactionAcquiredDisposedCode") != "A":
            continue
        shares = _to_float(_value(txn, "transactionAmounts/transactionShares"))
        price = _to_float(_value(txn, "transactionAmounts/transactionPricePerShare"))
        total_shares += shares
        total_value += shares * price
        date = _value(txn, "transactionDate")
        if date and date not in dates:
            dates.append(date)
        after = _value(txn, "postTransactionAmounts/sharesOwnedFollowingTransaction")
        if after:
            owned_after = _to_float(after)
    if total_shares <= 0 or total_value <= 0:
        return None

    names, titles = [], []
    is_officer = is_director = is_ten_pct = False
    for owner in doc.findall("reportingOwner"):
        name = _text(owner.find("reportingOwnerId/rptOwnerName"))
        if name:
            names.append(name)
        rel = owner.find("reportingOwnerRelationship")
        if rel is not None:
            is_officer = is_officer or _is_true(_value(rel, "isOfficer"))
            is_director = is_director or _is_true(_value(rel, "isDirector"))
            is_ten_pct = is_ten_pct or _is_true(_value(rel, "isTenPercentOwner"))
            title = _value(rel, "officerTitle")
            if title:
                titles.append(title)
    if not (is_officer or is_director or is_ten_pct):
        return None

    footnotes = [_text(fn) for fn in doc.findall("footnotes/footnote") if _text(fn)]
    pre_planned = _is_true(_text(doc.find("aff10b5One"))) or any(
        "10b5-1" in fn for fn in footnotes
    )
    return {
        "ticker": _value(doc.find("issuer"), "issuerTradingSymbol").upper(),
        "issuer_name": _value(doc.find("issuer"), "issuerName"),
        "insider_name": "; ".join(names),
        "insider_title": "; ".join(titles) or (
            "Director" if is_director else "10% owner" if is_ten_pct else ""
        ),
        "is_officer": is_officer,
        "is_director": is_director,
        "is_ten_percent_owner": is_ten_pct,
        "transaction_dates": dates,
        "total_shares": round(total_shares, 4),
        "avg_price": round(total_value / total_shares, 4),
        "total_value": round(total_value, 2),
        "shares_owned_after": owned_after,
        "pre_planned_10b5_1": pre_planned,
        "footnotes": footnotes,
    }


def fetch_new_insider_buys(
    min_total_value: float = 100_000.0,
    max_filings: int = 100,
    mark_seen: bool = True,
    include_seen: bool = False,
) -> List[InsiderBuy]:
    """Scan the current EDGAR Form 4 feed and return open-market insider buys
    of at least min_total_value not reported by a previous run."""
    seen = _load_seen()
    seen_set = set(seen)
    buys: List[InsiderBuy] = []
    for filing in _list_filings(max_filings):
        accession = filing["accession"]
        if not include_seen and accession in seen_set:
            continue
        if accession not in seen_set:
            seen.append(accession)
            seen_set.add(accession)
        try:
            xml_url = _find_ownership_xml_url(filing["filing_url"])
            if not xml_url:
                continue
            parsed = _parse_form4(ET.fromstring(_get(xml_url)))
        except (urllib.error.URLError, ET.ParseError, ValueError, KeyError):
            continue  # skip malformed/unreachable filings; never guess
        if not parsed or not parsed["ticker"] or parsed["ticker"] in ("NONE", "N/A"):
            continue
        if parsed["total_value"] < min_total_value:
            continue
        buys.append(InsiderBuy(
            filed_at=filing["filed_at"],
            accession_no=accession,
            filing_url=filing["filing_url"],
            **parsed,
        ))
    if mark_seen:
        _save_seen(seen)
    return buys


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fetch new SEC Form 4 insider buys")
    parser.add_argument("--min-value", type=float, default=100_000.0)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--include-seen", action="store_true",
                        help="also return filings already seen in previous runs")
    parser.add_argument("--no-mark-seen", action="store_true",
                        help="do not record these filings as seen")
    cli = parser.parse_args()
    results = fetch_new_insider_buys(
        min_total_value=cli.min_value,
        max_filings=cli.limit,
        mark_seen=not cli.no_mark_seen,
        include_seen=cli.include_seen,
    )
    print(json.dumps([to_dict(b) for b in results], indent=2))
