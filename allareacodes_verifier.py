import argparse
import csv
import re
import time
import urllib.error
import urllib.request
from typing import Dict, List, Optional, Tuple

from us_phone_generator import USPhoneNumberGenerator


ALL_AREA_CODES_BASE_URL = "https://www.allareacodes.com"
INTELIUS_BASE_URL = "https://www.intelius.com/reverse-phone-lookup"
WHITEPAGES_BASE_URL = "https://www.whitepages.com/phone"
WIREFLY_BASE_URL = "https://www.wirefly.com/area-codes"
MOBILE_SIGNAL_RE = re.compile(r"\b(mobile|cell\s*phone|wireless|cellular)\b", re.IGNORECASE)


def build_intelius_lookup_url(raw_number_10: str) -> str:
    return f"{INTELIUS_BASE_URL}/{raw_number_10}"


def build_whitepages_lookup_url(raw_number_10: str) -> str:
    return (
        f"{WHITEPAGES_BASE_URL}/1-"
        f"{raw_number_10[:3]}-{raw_number_10[3:6]}-{raw_number_10[6:10]}"
    )


def build_wirefly_lookup_url(area_code: str) -> str:
    return f"{WIREFLY_BASE_URL}/{area_code}"


def fetch_web_page(url: str, timeout: float) -> Tuple[str, str, str]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="ignore")
            return ("online_verified", str(response.status), body)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore") if hasattr(exc, "read") else ""
        if exc.code == 403:
            if "datadome" in body.lower() or "x-datadome" in str(exc.headers).lower():
                return ("blocked", "403", body)
            return ("forbidden", "403", body)
        return ("http_error", str(exc.code), body)
    except Exception as exc:
        return ("request_error", "", str(exc))


def has_mobile_signal(text: str) -> bool:
    return bool(MOBILE_SIGNAL_RE.search(text or ""))


def normalize_to_e164_us(value: str) -> Optional[str]:
    raw = (value or "").strip()
    if not raw:
        return None

    if raw.startswith("+"):
        digits = "+" + re.sub(r"\D", "", raw[1:])
    else:
        digits_only = re.sub(r"\D", "", raw)
        if len(digits_only) == 10:
            digits = "+1" + digits_only
        elif len(digits_only) == 11 and digits_only.startswith("1"):
            digits = "+" + digits_only
        else:
            return None

    if re.fullmatch(r"\+[1-9]\d{7,14}", digits):
        return digits
    return None


def csv_rows_from_input(path: str) -> List[str]:
    rows: List[str] = []
    with open(path, newline="", encoding="utf-8") as infile:
        reader = csv.reader(infile)
        for row in reader:
            if not row:
                continue
            first = (row[0] or "").strip()
            if not first or first.lower() in {"phone", "phone_number", "number", "input_number"}:
                continue
            rows.append(first)
    return rows


def all_local_area_codes() -> Dict[str, str]:
    area_to_state: Dict[str, str] = {}
    for state in USPhoneNumberGenerator.get_states():
        for code in USPhoneNumberGenerator.get_area_codes_for_state(state):
            area_to_state[str(code)] = state
    return area_to_state


def fetch_allareacodes_page(area_code: str, timeout: float) -> Tuple[str, str, str]:
    url = f"{ALL_AREA_CODES_BASE_URL}/{area_code}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="ignore")
            return ("online_verified", str(response.status), body)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore") if hasattr(exc, "read") else ""
        if exc.code == 403:
            if "datadome" in body.lower() or "x-datadome" in str(exc.headers).lower():
                return ("blocked", "403", body)
            return ("forbidden", "403", body)
        return ("http_error", str(exc.code), body)
    except Exception as exc:
        return ("request_error", "", str(exc))


def extract_title(html_text: str) -> str:
    match = re.search(r"<title>(.*?)</title>", html_text, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    return re.sub(r"\s+", " ", match.group(1)).strip()


def verify_number(
    input_number: str,
    area_map: Dict[str, str],
    timeout: float,
    delay: float,
    selected_sites: Dict[str, bool],
    carrier: str,
) -> Dict[str, str]:
    normalized = normalize_to_e164_us(input_number)
    if not normalized:
        return {
            "input_number": input_number,
            "exact_number": "",
            "area_code": "",
            "local_area_valid": "False",
            "local_state": "",
            "requested_carrier": carrier,
            "source": "",
            "verification_status": "invalid_format",
            "http_status": "",
            "online_title": "",
            "source_url": "",
            "connected_sites": "0",
            "internet_connectivity": "offline",
            "mobile_signal": "False",
            "allareacodes_url": "",
            "intelius_url": "",
            "whitepages_url": "",
            "wirefly_url": "",
            "error": "Invalid US number format",
        }

    area_code = normalized[-10:-7]
    local_state = area_map.get(area_code, "")
    local_valid = bool(local_state)

    allareacodes_url = (
        f"{ALL_AREA_CODES_BASE_URL}/{area_code}"
        if selected_sites.get("allareacodes", False)
        else ""
    )
    intelius_url = (
        build_intelius_lookup_url(normalized[-10:])
        if selected_sites.get("intelius", False)
        else ""
    )
    whitepages_url = (
        build_whitepages_lookup_url(normalized[-10:])
        if selected_sites.get("whitepages", False)
        else ""
    )
    wirefly_url = (
        build_wirefly_lookup_url(area_code)
        if selected_sites.get("wirefly", False)
        else ""
    )

    source_names: List[str] = []
    source_urls: List[str] = []
    page_bodies: List[str] = []
    connected_sites = 0
    if allareacodes_url:
        source_names.append("allareacodes.com")
        source_urls.append(allareacodes_url)
    if intelius_url:
        source_names.append("intelius.com")
        source_urls.append(intelius_url)
    if whitepages_url:
        source_names.append("whitepages.com")
        source_urls.append(whitepages_url)
    if wirefly_url:
        source_names.append("wirefly.com")
        source_urls.append(wirefly_url)

    status = "website_linked"
    http_status = ""
    payload = ""
    title = ""
    if allareacodes_url:
        status, http_status, payload = fetch_allareacodes_page(area_code, timeout)
        if status == "online_verified":
            connected_sites += 1
            page_bodies.append(payload)
            title = extract_title(payload)

    if intelius_url:
        int_status, _, int_payload = fetch_web_page(intelius_url, timeout)
        if int_status == "online_verified":
            connected_sites += 1
            page_bodies.append(int_payload)

    if whitepages_url:
        wp_status, _, wp_payload = fetch_web_page(whitepages_url, timeout)
        if wp_status == "online_verified":
            connected_sites += 1
            page_bodies.append(wp_payload)

    if wirefly_url:
        wf_status, _, wf_payload = fetch_web_page(wirefly_url, timeout)
        if wf_status == "online_verified":
            connected_sites += 1
            page_bodies.append(wf_payload)

    source_url = ";".join(source_urls)
    mobile_signal = has_mobile_signal("\n".join(page_bodies))
    if connected_sites >= 2:
        internet_connectivity = "best"
    elif connected_sites == 1:
        internet_connectivity = "limited"
    else:
        internet_connectivity = "offline"

    row = {
        "input_number": input_number,
        "exact_number": normalized,
        "area_code": area_code,
        "local_area_valid": str(local_valid),
        "local_state": local_state,
        "requested_carrier": carrier,
        "source": "|".join(source_names),
        "verification_status": status,
        "http_status": http_status,
        "online_title": title,
        "source_url": source_url,
        "connected_sites": str(connected_sites),
        "internet_connectivity": internet_connectivity,
        "mobile_signal": "True" if mobile_signal else "False",
        "allareacodes_url": allareacodes_url,
        "intelius_url": intelius_url,
        "whitepages_url": whitepages_url,
        "wirefly_url": wirefly_url,
        "error": "",
    }

    if selected_sites.get("allareacodes", False) and status in {"blocked", "forbidden", "http_error", "request_error"}:
        if status == "blocked":
            row["error"] = "allareacodes.com blocked this environment (anti-bot protection)"
        elif status == "forbidden":
            row["error"] = "allareacodes.com returned 403"
        elif status == "http_error":
            row["error"] = f"HTTP {http_status} from allareacodes.com"
        else:
            row["error"] = payload

    if delay > 0:
        time.sleep(delay)

    return row


def verify_all(
    input_file: str,
    output_file: str,
    timeout: float,
    delay: float,
    selected_sites: Dict[str, bool],
    carrier: str,
    internet_mobile_only: bool,
    min_connected_sites: int,
) -> Dict[str, int]:
    area_map = all_local_area_codes()
    input_numbers = csv_rows_from_input(input_file)

    rows = [
        verify_number(number, area_map, timeout, delay, selected_sites, carrier)
        for number in input_numbers
    ]

    if internet_mobile_only:
        rows = [
            row
            for row in rows
            if row["mobile_signal"] == "True" and int(row["connected_sites"]) >= min_connected_sites
        ]

    with open(output_file, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(
            [
                "input_number",
                "exact_number",
                "area_code",
                "local_area_valid",
                "local_state",
                "requested_carrier",
                "source",
                "verification_status",
                "http_status",
                "online_title",
                "source_url",
                "connected_sites",
                "internet_connectivity",
                "mobile_signal",
                "allareacodes_url",
                "intelius_url",
                "whitepages_url",
                "wirefly_url",
                "error",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row["input_number"],
                    row["exact_number"],
                    row["area_code"],
                    row["local_area_valid"],
                    row["local_state"],
                    row["requested_carrier"],
                    row["source"],
                    row["verification_status"],
                    row["http_status"],
                    row["online_title"],
                    row["source_url"],
                    row["connected_sites"],
                    row["internet_connectivity"],
                    row["mobile_signal"],
                    row["allareacodes_url"],
                    row["intelius_url"],
                    row["whitepages_url"],
                    row["wirefly_url"],
                    row["error"],
                ]
            )

    return {
        "input_count": len(input_numbers),
        "written_count": len(rows),
        "online_verified": sum(1 for r in rows if r["verification_status"] == "online_verified"),
        "blocked": sum(1 for r in rows if r["verification_status"] == "blocked"),
        "local_valid": sum(1 for r in rows if r["local_area_valid"] == "True"),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify US numbers using selected website lookups and local area-code validation."
    )
    parser.add_argument("--input", required=True, help="Input CSV file path (first column must be phone numbers)")
    parser.add_argument("--output", default="verified_numbers_allareacodes.csv", help="Output CSV file path")
    parser.add_argument("--timeout", type=float, default=12.0, help="HTTP timeout in seconds")
    parser.add_argument("--delay", type=float, default=0.2, help="Delay between requests in seconds")
    parser.add_argument("--carrier", default="Any", help="Requested carrier label to include in output")
    parser.add_argument("--no-allareacodes", action="store_true", help="Disable allareacodes.com lookup links")
    parser.add_argument("--no-intelius", action="store_true", help="Disable intelius.com lookup links")
    parser.add_argument("--no-whitepages", action="store_true", help="Disable whitepages.com lookup links")
    parser.add_argument("--no-wirefly", action="store_true", help="Disable wirefly.com lookup links")
    parser.add_argument(
        "--internet-mobile-only",
        action="store_true",
        help="Keep only rows with internet mobile signal and minimum connected website checks",
    )
    parser.add_argument(
        "--min-connected-sites",
        type=int,
        default=2,
        help="Minimum number of connected website checks required in --internet-mobile-only mode",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    selected_sites = {
        "allareacodes": not args.no_allareacodes,
        "intelius": not args.no_intelius,
        "whitepages": not args.no_whitepages,
        "wirefly": not args.no_wirefly,
    }
    if not any(selected_sites.values()):
        raise SystemExit("At least one website must be enabled. Remove one or more --no-* flags.")

    started = time.time()
    summary = verify_all(
        input_file=args.input,
        output_file=args.output,
        timeout=max(1.0, args.timeout),
        delay=max(0.0, args.delay),
        selected_sites=selected_sites,
        carrier=(args.carrier or "Any").strip() or "Any",
        internet_mobile_only=bool(args.internet_mobile_only),
        min_connected_sites=max(0, int(args.min_connected_sites)),
    )
    elapsed = time.time() - started

    print("Verification complete")
    print(f"Input numbers:      {summary['input_count']}")
    print(f"Rows written:       {summary['written_count']}")
    print(f"Online verified:    {summary['online_verified']}")
    print(f"Blocked requests:   {summary['blocked']}")
    print(f"Local area valid:   {summary['local_valid']}")
    print(f"Elapsed:            {elapsed:.2f}s")
    print(f"Output file:        {args.output}")


if __name__ == "__main__":
    main()
