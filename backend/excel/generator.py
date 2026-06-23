from datetime import datetime
from pathlib import Path

import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from config import EXPORT_DIR


SUMMARY_COLUMNS = {
    "Bill Name",
    "Invoice Number",
    "Date",
    "Customer",
    "Buyer",
    "Phone",
    "GST Number",
    "GST Amount",
    "Tax",
    "Discount",
    "Total",
    "Payment Method",
}

ROW_DETAIL_COLUMNS = {"Item", "Description", "Qty", "Rate", "Amount"}


def _safe_columns(columns: list[str], rows: list[dict]) -> list[str]:
    detected = list(dict.fromkeys(columns or []))
    for row in rows:
        for key in row.keys():
            if key not in detected:
                detected.append(key)
    return detected or ["Data"]


def _has_value(value: object) -> bool:
    return value is not None and str(value).strip() != ""


def _split_summary_and_raw(rows: list[dict], columns: list[str]) -> tuple[dict[str, str], list[str]]:
    summary: dict[str, str] = {}
    raw_columns: list[str] = []

    for column in columns:
        values = [str(row.get(column, "")).strip() for row in rows if _has_value(row.get(column))]
        unique_values = set(values)

        if values and len(unique_values) == 1 and column not in ROW_DETAIL_COLUMNS and (column in SUMMARY_COLUMNS or len(rows) > 1):
            summary[column] = values[0]
        else:
            raw_columns.append(column)

    return summary, raw_columns or columns


def _style_sheet(sheet, header_fill: PatternFill) -> None:
    for cell in sheet[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.alignment = Alignment(horizontal="center")
        cell.fill = header_fill

    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions

    for column_cells in sheet.columns:
        max_length = max(len(str(cell.value or "")) for cell in column_cells)
        column_letter = get_column_letter(column_cells[0].column)
        sheet.column_dimensions[column_letter].width = min(max(max_length + 2, 12), 50)


def generate_excel_file(rows: list[dict], columns: list[str] | None = None, filename_prefix: str = "export") -> Path:
    safe_rows = rows or [{}]
    safe_columns = _safe_columns(columns or [], safe_rows)
    summary_values, raw_columns = _split_summary_and_raw(safe_rows, safe_columns)
    frame = pd.DataFrame(safe_rows)

    for column in raw_columns:
        if column not in frame.columns:
            frame[column] = ""
    frame = frame[raw_columns]

    filename = f"{filename_prefix}_{datetime.now().strftime('%Y%m%d')}.xlsx"
    output_path = EXPORT_DIR / filename

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        frame.to_excel(writer, sheet_name="Raw Data", index=False)
        workbook = writer.book
        sheet = writer.sheets["Raw Data"]
        header_fill = PatternFill("solid", fgColor="1E293B")
        _style_sheet(sheet, header_fill)

        summary = workbook.create_sheet("Summary")
        summary.append(["Metric", "Value"])
        for key, value in summary_values.items():
            summary.append([key, value])
        summary.append(["Raw Rows", len(frame)])
        summary.append(["Raw Columns", len(raw_columns)])
        summary.append(["Moved To Summary", len(summary_values)])
        summary.append(["Generated At", datetime.now().isoformat(timespec="seconds")])
        _style_sheet(summary, header_fill)

    return output_path
