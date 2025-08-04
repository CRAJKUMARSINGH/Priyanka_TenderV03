#!/usr/bin/env python3
"""
bulk_safe.py
Hardened bulk generator + ZIP packager.
Logs every failure but never stops the pipeline.
"""
import os
import shutil
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# ------------------------------------------------------------------
# Import your real generators
# ------------------------------------------------------------------
from document_generator import DocumentGenerator as WordGen
from latex_pdf_generator import LatexPDFGenerator as LatexGen   # adjust if name differs
from date_utils import DateUtils

OUT_DIR       = Path("output")
LOG_FILE      = OUT_DIR / "bulk_errors.log"
ZIP_NAME      = OUT_DIR / f"tender_package_{datetime.now():%Y%m%d_%H%M%S}.zip"

# helpers ------------------------------------------------------------
def log_error(msg: str):
    OUT_DIR.mkdir(exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as lf:
        lf.write(f"{datetime.now():%F %T}  {msg}\n")

def safe_call(fn, *args, **kw):
    """invoke fn, return bytes on success else None + log"""
    try:
        return fn(*args, **kw)
    except Exception as exc:
        log_error(f"{fn.__name__} failed: {exc}")
        return None

# ------------------------------------------------------------------
# Main driver
# ------------------------------------------------------------------
def run_bulk(data: Dict[str, Any], bidders: List[Dict[str, Any]]):
    word_gen = WordGen()
    latex_gen = LatexGen()

    tmp_root = Path(tempfile.mkdtemp(prefix="tender_"))
    files_created = []

    # 1. Word docs --------------------------------------------------
    for suffix, meth in (
        ("comparative_statement.docx", word_gen.generate_comparative_statement_doc),
        ("scrutiny_sheet.docx",        word_gen.generate_scrutiny_sheet_doc),
    ):
        blob = safe_call(meth, data, bidders)
        if blob:
            f = tmp_root / suffix
            f.write_bytes(blob)
            files_created.append(f)

    # 2. PDFs -------------------------------------------------------
    if bidders:
        l1 = min(bidders, key=lambda x: x.get("bid_amount", float("inf")))
    else:
        l1 = {"name": "No bidder", "bid_amount": 0, "percentage": 0}

    for suffix, meth, *args in (
        ("comparative_statement.pdf", latex_gen.generate_comparative_statement_pdf, data, bidders),
        ("scrutiny_sheet.pdf",        latex_gen.generate_scrutiny_sheet_pdf,        data, bidders),
        ("letter_of_acceptance.pdf",  latex_gen.generate_letter_of_acceptance_pdf,  data, l1),
        ("work_order.pdf",            latex_gen.generate_work_order_pdf,            data, l1),
    ):
        blob = safe_call(meth, *args)
        if blob:
            f = tmp_root / suffix
            f.write_bytes(blob)
            files_created.append(f)

    # 3. Fallback so ZIP is never empty ----------------------------
    if not files_created:
        log_error("No successful documents – creating fallback.txt")
        fallback = tmp_root / "README.txt"
        fallback.write_text(
            "All generators failed.\nCheck bulk_errors.log for details."
        )
        files_created.append(fallback)

    # 4. ZIP --------------------------------------------------------
    OUT_DIR.mkdir(exist_ok=True)
    with zipfile.ZipFile(ZIP_NAME, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in files_created:
            zf.write(file, file.name)

    # 5. Cleanup ----------------------------------------------------
    shutil.rmtree(tmp_root)
    print(f"✅ Package ready: {ZIP_NAME}")
    if LOG_FILE.exists():
        print(f"⚠️  Some errors logged: {LOG_FILE}")

# ------------------------------------------------------------------
# Sample stub – replace with your real JSON / DB fetch
# ------------------------------------------------------------------
if __name__ == "__main__":
    sample_work = {
        "work_name": "Sample Electrical Work",
        "nit_number": "NIT/2025/01",
        "work_info": {
            "estimated_cost": 1_000_000,
            "earnest_money": "20,000",
            "time_of_completion": "6 months",
            "date": "2025-08-03",
        },
    }
    sample_bidders = [
        {"name": "ABC Contractors", "bid_amount": 950_000, "percentage": -5.0},
        {"name": "XYZ Enterprises", "bid_amount": 980_000, "percentage": -2.0},
    ]

    run_bulk(sample_work, sample_bidders)
