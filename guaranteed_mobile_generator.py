import argparse
import csv
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, cast

from us_phone_generator import USPhoneNumberGenerator


LOOKUP_URL = "https://api.telnyx.com/v2/number_lookup"


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


def telnyx_lookup(e164_number: str, api_key: str, timeout: float) -> Dict[str, str]:
    params = urllib.parse.urlencode({"phone_number": e164_number, "type": "carrier"})
    url = f"{LOOKUP_URL}?{params}"
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "USNUM-Mobile-Generator/1.0",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8", errors="ignore"))
            data = payload.get("data") or {}
            carrier = data.get("carrier") or {}
            line_type = (carrier.get("type") or "").lower()
            is_mobile = line_type == "mobile"
            return {
                "status": "ok",
                "http_status": str(response.status),
                "line_type": line_type,
                "carrier": carrier.get("name") or "",
                "exact_number": data.get("phone_number") or data.get("e164_phone_number") or e164_number,
                "connectivity": "connected",
                "verified_mobile": "True" if is_mobile else "False",
                "error": "",
            }
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore") if hasattr(exc, "read") else ""
        return {
            "status": "http_error",
            "http_status": str(exc.code),
            "line_type": "",
            "carrier": "",
            "exact_number": e164_number,
            "connectivity": "lookup_failed",
            "verified_mobile": "False",
            "error": body or f"HTTP {exc.code}",
        }
    except Exception as exc:
        return {
            "status": "request_error",
            "http_status": "",
            "line_type": "",
            "carrier": "",
            "exact_number": e164_number,
            "connectivity": "request_error",
            "verified_mobile": "False",
            "error": str(exc),
        }


def format_number(raw_10: str) -> str:
    return f"{raw_10[:3]}-{raw_10[3:6]}-{raw_10[6:]}"


def generate_verified_mobile_numbers(
    state: str,
    count: int,
    api_key: str,
    timeout: float,
    delay: float,
    max_attempts: int,
) -> Dict[str, object]:
    generated: List[Dict[str, str]] = []
    attempts = 0
    connected = 0
    mobile_hits = 0

    while len(generated) < count and attempts < max_attempts:
        raw = USPhoneNumberGenerator.generate_single_number(state)
        attempts += 1

        e164 = normalize_to_e164_us(raw)
        if not e164:
            continue

        lookup = telnyx_lookup(e164, api_key, timeout)

        if lookup["connectivity"] == "connected":
            connected += 1
        if lookup["verified_mobile"] == "True":
            mobile_hits += 1

        if lookup["verified_mobile"] == "True" and lookup["connectivity"] == "connected":
            generated.append(
                {
                    "input_number": format_number(raw),
                    "exact_number": lookup["exact_number"],
                    "state": state,
                    "area_code": raw[:3],
                    "verified_mobile": "True",
                    "line_type": lookup["line_type"],
                    "carrier": lookup["carrier"],
                    "connectivity": lookup["connectivity"],
                    "http_status": lookup["http_status"],
                    "error": "",
                }
            )

        if delay > 0:
            time.sleep(delay)

    return {
        "rows": generated,
        "attempts": attempts,
        "connected": connected,
        "mobile_hits": mobile_hits,
    }


def write_csv(path: str, rows: List[Dict[str, str]]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(
            [
                "input_number",
                "exact_number",
                "state",
                "area_code",
                "verified_mobile",
                "line_type",
                "carrier",
                "connectivity",
                "http_status",
                "error",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row["input_number"],
                    row["exact_number"],
                    row["state"],
                    row["area_code"],
                    row["verified_mobile"],
                    row["line_type"],
                    row["carrier"],
                    row["connectivity"],
                    row["http_status"],
                    row["error"],
                ]
            )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate US phone numbers and keep only API-verified mobile numbers with connected lookup status."
    )
    parser.add_argument("--state", required=True, help="US state code, e.g. TX")
    parser.add_argument("--count", type=int, required=True, help="Number of verified mobile rows to output")
    parser.add_argument("--output", default="verified_mobile_guaranteed.csv", help="Output CSV file path")
    parser.add_argument("--api-key", default=os.getenv("TELNYX_API_KEY", ""), help="Telnyx API key")
    parser.add_argument("--timeout", type=float, default=12.0, help="Lookup timeout in seconds")
    parser.add_argument("--delay", type=float, default=0.1, help="Delay between lookups in seconds")
    parser.add_argument("--max-attempts", type=int, default=5000, help="Maximum generated numbers to attempt")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    state = (args.state or "").strip().upper()
    if state not in USPhoneNumberGenerator.get_states():
        raise SystemExit(f"Invalid state: {state}")

    if args.count <= 0:
        raise SystemExit("--count must be > 0")

    if not args.api_key:
        raise SystemExit("Missing API key. Set TELNYX_API_KEY or pass --api-key.")

    started = time.time()
    result = generate_verified_mobile_numbers(
        state=state,
        count=args.count,
        api_key=args.api_key,
        timeout=max(1.0, args.timeout),
        delay=max(0.0, args.delay),
        max_attempts=max(args.count, args.max_attempts),
    )

    rows = cast(List[Dict[str, str]], result["rows"])
    attempts = cast(int, result["attempts"])
    connected = cast(int, result["connected"])
    mobile_hits = cast(int, result["mobile_hits"])
    write_csv(args.output, rows)

    elapsed = time.time() - started
    print("Guaranteed mobile generation complete")
    print(f"State:             {state}")
    print(f"Requested count:   {args.count}")
    print(f"Written rows:      {len(rows)}")
    print(f"Attempts:          {attempts}")
    print(f"Connected lookups: {connected}")
    print(f"Mobile hits:       {mobile_hits}")
    print(f"Elapsed:           {elapsed:.2f}s")
    print(f"Output file:       {args.output}")

    if len(rows) < args.count:
        print("Warning: Could not reach requested count within max attempts. Increase --max-attempts.")


if __name__ == "__main__":
    main()
