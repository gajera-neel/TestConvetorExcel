from datetime import datetime
from pathlib import Path

import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill

from config import EXPORT_DIR


def _safe_columns(columns: list[str], rows: list[dict]) -> list[str]:
    detected = list(dict.fromkeys(columns or []))
    for row in rows:
        for key in row.keys():
            if key not in detected:
                detected.append(key)
    return detected or ["Data"]


def generate_excel_file(rows: list[dict], columns: list[str] | None = None, filename_prefix: str = "export") -> Path:
    safe_rows = rows or [{}]
    safe_columns = _safe_columns(columns or [], safe_rows)
    frame = pd.DataFrame(safe_rows)

    for column in safe_columns:
        if column not in frame.columns:
            frame[column] = ""
    frame = frame[safe_columns]

    filename = f"{filename_prefix}_{datetime.now().strftime('%Y%m%d')}.xlsx"
    output_path = EXPORT_DIR / filename

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        frame.to_excel(writer, sheet_name="Raw Data", index=False)
        workbook = writer.book
        sheet = writer.sheets["Raw Data"]
        header_fill = PatternFill("solid", fgColor="1E293B")

        for cell in sheet[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.alignment = Alignment(horizontal="center")
            cell.fill = header_fill

        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = sheet.dimensions

        for column_cells in sheet.columns:
            max_length = max(len(str(cell.value or "")) for cell in column_cells)
            sheet.column_dimensions[column_cells[0].column_letter].width = min(max(max_length + 2, 12), 50)

        summary = workbook.create_sheet("Summary")
        summary.append(["Metric", "Value"])
        summary.append(["Rows", len(frame)])
        summary.append(["Columns", len(safe_columns)])
        summary.append(["Generated At", datetime.now().isoformat(timespec="seconds")])
        for cell in summary[1]:
            cell.font = Font(bold=True)

    return output_path
