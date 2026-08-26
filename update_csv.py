from __future__ import annotations

import csv
import io
import re
import sys
import urllib.request
from collections import Counter
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader


SOURCE_URL = "https://www.wa.gov.au/media/48368/download"
OUTPUT_PATH = Path("data/wa_security_officers.csv")

# Every licence row in the WA Police document finishes with a dd/mm/yyyy date.
ROW_PATTERN = re.compile(
    r"^\s*(?P<licence>\d+)\s+(?P<name>.+?)\s+"
    r"(?P<expiry>\d{2}/\d{2}/\d{4})\s*$"
)


def download_pdf() -> bytes:
    request = urllib.request.Request(
        SOURCE_URL,
        headers={"User-Agent": "WA-security-register-CSV-updater/1.0"},
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        content = response.read()

    if not content.startswith(b"%PDF-"):
        raise RuntimeError("The WA download did not return a PDF file.")

    return content


def extract_rows(pdf_content: bytes) -> list[tuple[str, str, str]]:
    reader = PdfReader(io.BytesIO(pdf_content))
    rows: list[tuple[str, str, str]] = []

    for page in reader.pages:
        text = page.extract_text() or ""
        for raw_line in text.splitlines():
            line = " ".join(raw_line.split())
            match = ROW_PATTERN.match(line)
            if not match:
                continue

            expiry = datetime.strptime(
                match.group("expiry"), "%d/%m/%Y"
            ).date()
            rows.append(
                (
                    match.group("licence"),
                    match.group("name").strip(),
                    expiry.isoformat(),
                )
            )

    return rows


def validate_rows(rows: list[tuple[str, str, str]]) -> None:
    # The current register has over 16,000 rows. This lower threshold prevents
    # a damaged or redesigned PDF from silently replacing the CSV.
    if len(rows) < 10_000:
        raise RuntimeError(
            f"Only {len(rows):,} rows were extracted; refusing to replace the CSV."
        )

    licences = [row[0] for row in rows]
    duplicates = sorted(
        licence for licence, count in Counter(licences).items() if count > 1
    )
    if duplicates:
        preview = ", ".join(duplicates[:10])
        raise RuntimeError(f"Duplicate licence numbers detected: {preview}")


def write_csv(rows: list[tuple[str, str, str]]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = OUTPUT_PATH.with_suffix(".csv.tmp")

    with temporary_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["Licence Number", "Full Name", "Expiry Date"])
        writer.writerows(rows)

    temporary_path.replace(OUTPUT_PATH)


def main() -> int:
    pdf_content = download_pdf()
    rows = extract_rows(pdf_content)
    validate_rows(rows)
    write_csv(rows)
    print(f"Wrote {len(rows):,} rows to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
