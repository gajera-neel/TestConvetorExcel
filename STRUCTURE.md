# Document To Excel AI Conversion

Modern full-stack demo app for uploading bills, invoices, receipts, PDFs, and scanned images, extracting dynamic data, editing raw rows, and downloading formatted Excel.

## Tech Stack

- Backend: Python FastAPI
- Frontend: Next.js, Tailwind CSS, TypeScript, Framer Motion
- OCR: Tesseract for images, pdfplumber plus OCR fallback for PDFs
- Data processing: Pandas
- Excel export: openpyxl
- UI: professional dashboard layout, dark sidebar, light content area, mobile friendly

## Main Flow

```text
Upload file
→ FastAPI detects file type
→ OCR / PDF extraction runs
→ Dynamic columns and rows are generated
→ User edits raw data table
→ Excel file is generated
→ User downloads .xlsx
```

## Project Structure

```text
project/
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── routes/
│   │   ├── upload.py
│   │   ├── dashboard.py
│   │   └── excel.py
│   ├── services/
│   │   ├── document_service.py
│   │   ├── dashboard_service.py
│   │   ├── excel_service.py
│   │   ├── history_service.py
│   │   └── temp_service.py
│   ├── excel/
│   │   └── generator.py
│   ├── ocr/
│   │   ├── image_ocr.py
│   │   └── pdf_ocr.py
│   ├── parsers/
│   │   └── dynamic_parser.py
│   ├── temp/
│   ├── uploads/
│   └── exports/
├── frontend/
│   ├── app/
│   │   ├── upload/
│   │   ├── dashboard/
│   │   └── excel-export/
│   ├── components/
│   ├── lib/
│   ├── package.json
│   └── tailwind.config.ts
├── samples/
├── requirements.txt
└── STRUCTURE.md
```

## Navigation Order

1. Upload
2. Dashboard
3. Excel Export

The root Next.js route redirects to `/upload`, so Upload opens first.

## Frontend Details

Frontend runs on Node.js with Next.js.

Important files:

- `frontend/app/upload/page.tsx`: upload, preview, OCR result, raw editable data table, generate Excel button.
- `frontend/app/dashboard/page.tsx`: metrics cards, charts, recent files.
- `frontend/app/excel-export/page.tsx`: final preview and Excel download.
- `frontend/components/AppShell.tsx`: sidebar and mobile navigation.
- `frontend/components/EditableDataTable.tsx`: dynamic columns, editable cells, add row, delete row, rename column, search, sort, pagination.
- `frontend/lib/api.ts`: connects frontend to FastAPI backend at `http://127.0.0.1:8000`.

Frontend libraries:

- `next`: React full-stack frontend framework.
- `react`, `react-dom`: UI library.
- `tailwindcss`: utility CSS styling.
- `framer-motion`: smooth UI animations.
- `typescript`: type safety.

Frontend storage:

- Latest extraction is saved in browser `localStorage`.
- No database is used.

## Backend Details

Backend runs on Python FastAPI.

Important files:

- `backend/main.py`: FastAPI app, CORS, route registration, static uploads.
- `backend/routes/upload.py`: upload and extract APIs.
- `backend/routes/dashboard.py`: dashboard API.
- `backend/routes/excel.py`: Excel download APIs.
- `backend/ocr/image_ocr.py`: image OCR using Tesseract and optional EasyOCR fallback.
- `backend/ocr/pdf_ocr.py`: PDF text extraction using pdfplumber and OCR fallback.
- `backend/parsers/dynamic_parser.py`: generates dynamic fields, columns, and rows.
- `backend/excel/generator.py`: creates formatted Excel files.
- `backend/services/temp_service.py`: temporary JSON sessions.

Backend libraries:

- `fastapi`: Python API framework.
- `uvicorn`: local API server.
- `python-multipart`: file upload support.
- `pytesseract`: Python wrapper for Tesseract OCR.
- `pillow`: image handling.
- `opencv-python`: image preprocessing.
- `pdfplumber`: PDF text extraction.
- `pypdfium2`: render scanned PDF pages for OCR fallback.
- `pandas`: table/data processing.
- `openpyxl`: Excel file generation and formatting.

Backend storage:

- `backend/uploads/`: uploaded files.
- `backend/temp/`: temporary JSON extraction sessions and history.
- `backend/exports/`: generated Excel files.
- No database is used.

## Backend APIs

### `POST /upload`

Uploads and analyzes a file.

```json
{
  "file_type": "txt",
  "detected_type": "invoice",
  "extracted_text": "...",
  "extracted_fields": {
    "columns": [],
    "rows": [],
    "fields": {}
  },
  "dashboard": {},
  "confidence": 0.9,
  "logs": []
}
```

### `POST /extract`

Re-runs extraction for an existing temporary upload session.

Input:

```json
{
  "session_id": "..."
}
```

### `GET /dashboard`

Returns dashboard metrics, uploads by day, amount trend, bill categories, and recent uploads.

### `GET /download-excel`

Creates and downloads a latest-history Excel report.

### `POST /generate-excel`

Creates and downloads an edited-table Excel file from temporary JSON/session data.

Input:

```json
{
  "session_id": "...",
  "columns": ["Date", "Party", "Amount"],
  "rows": [
    {
      "Date": "21/06/2026",
      "Party": "Demo Vendor",
      "Amount": "1000"
    }
  ]
}
```

Excel sheets:

- Raw Data
- Summary
- Dashboard Metrics

## Run Project Step By Step

Use two terminals: one for backend and one for frontend.

### 1. Install dependencies

Python dependencies:

```powershell
cd D:\project
python -m pip install -r requirements.txt
```

Node/Next.js dependencies:

```powershell
cd D:\project\frontend
npm install
```

### 2. Check Tesseract OCR

Tesseract is required for image OCR.

```powershell
& "C:\Program Files\Tesseract-OCR\tesseract.exe" --version
```

### 3. Start backend

```powershell
cd D:\project\backend
python -m uvicorn main:app --reload
```

Test:

```text
http://127.0.0.1:8000/
```

Expected response:

```json
{"message":"Document Intelligence API is running"}
```

### 4. Start frontend

```powershell
cd D:\project\frontend
npm run dev
```

Open:

```text
http://127.0.0.1:3000/upload
```

Other pages:

```text
http://127.0.0.1:3000/dashboard
http://127.0.0.1:3000/excel-export
```

## How Frontend And Backend Connect

The frontend API helper is:

```text
frontend/lib/api.ts
```

It calls:

```text
http://127.0.0.1:8000
```

Backend must be running before upload/extract/export works.

## Excel Notes

Excel files are generated with:

- Bold headers
- Auto column width
- Filters
- Frozen top row
- `.xlsx` format

Generated files are saved in:

```text
backend/exports/
```

## UI Notes

Current UI style:

- Professional admin dashboard
- Dark sidebar
- Light content area
- Blue active states
- White cards
- Mobile top navigation
- Responsive upload/review/export pages

## Test Files

Upload these first:

- `samples/sample_bill.txt`
- `samples/normal_document.txt`
- `samples/large_sample_bill.txt`

Use `sample_bill.txt` to test Upload, Dashboard, and Excel Download.

## Common Errors

### Frontend opens but upload fails

Backend is probably not running. Start:

```powershell
cd D:\project\backend
python -m uvicorn main:app --reload
```

### Image OCR fails

Check Tesseract:

```powershell
& "C:\Program Files\Tesseract-OCR\tesseract.exe" --version
```

### UI looks unstyled

Restart frontend:

```powershell
cd D:\project\frontend
npm run dev
```

Then hard refresh browser with `Ctrl + F5`.
