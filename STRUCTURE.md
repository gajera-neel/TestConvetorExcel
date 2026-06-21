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
- `frontend/components/EditableDataTable.tsx`: dynamic columns, editable cells, add row, delete row, rename column, search, sort, pagination, table-only vertical and horizontal scrolling.
- `frontend/lib/api.ts`: connects frontend to FastAPI backend using `NEXT_PUBLIC_API_URL`, with local fallback to `http://127.0.0.1:8000`.

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

## How Frontend And Backend Connect Locally

The frontend API helper is:

```text
frontend/lib/api.ts
```

It calls this by default while developing locally:

```text
http://127.0.0.1:8000
```

Backend must be running before upload/extract/export works.

For deployment, set:

```text
NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com
```

Current deployed backend URL:

```text
https://test-convetor-excel-backend.onrender.com
```

## Deploy Project Online Step By Step

This project needs two deployments:

1. Backend API on Render.
2. Frontend website on Vercel.

The frontend must know the backend URL through `NEXT_PUBLIC_API_URL`.

### 1. Push Code To GitHub

Initialize and push the repository:

```powershell
cd D:\project
git init
git add .
git commit -m "Initial commit for document to Excel MVP."
git branch -M main
git remote add origin https://github.com/gajera-neel/TestConvetorExcel.git
git push -u origin main
```

The project is currently pushed here:

```text
https://github.com/gajera-neel/TestConvetorExcel
```

### 2. Deploy Backend On Render

Open:

```text
https://render.com
```

Choose:

```text
New + -> Web Service
```

Do not choose Static Site, PostgreSQL, or Background Worker.

Use these settings:

```text
Repository: TestConvetorExcel
Branch: main
Runtime: Python 3
Region: Singapore
Instance Type: Free
Root Directory: leave empty
Build Command: pip install -r requirements.txt
Start Command: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
Environment Variables: leave empty
```

Click:

```text
Deploy Web Service
```

After deploy, open the Render URL. Expected response:

```json
{"message":"Document Intelligence API is running"}
```

Current live backend:

```text
https://test-convetor-excel-backend.onrender.com
```

### 3. Deploy Frontend On Vercel

Open:

```text
https://vercel.com
```

Choose:

```text
Add New -> Project
```

Import:

```text
TestConvetorExcel
```

Use these settings:

```text
Application Preset / Framework Preset: Next.js
Root Directory: frontend
Install Command: npm install
Build Command: npm run build
Output Directory: leave empty / Next.js default
```

Add environment variable:

```text
Key: NEXT_PUBLIC_API_URL
Value: https://test-convetor-excel-backend.onrender.com
Environment: Production and Preview
```

If Vercel shows Development separately, it can be ignored for production deployment.

Click:

```text
Deploy
```

Current live frontend:

```text
https://test-convetor-excel.vercel.app
```

### 4. Fix Common Vercel Deployment Error

If Vercel shows:

```text
No Output Directory named "public" found after the Build completed.
```

Fix:

1. Go to Vercel project.
2. Open `Settings`.
3. Open `Build and Deployment`.
4. Set `Framework Preset` to `Next.js`.
5. Turn off Output Directory override.
6. Output Directory should be empty / Next.js default, not `public`.
7. Save.
8. Go to `Deployments`.
9. Redeploy the latest failed deployment.

### 5. Test Live Website

Open:

```text
https://test-convetor-excel.vercel.app
```

Test in this order:

1. Upload `samples/sample_bill.txt`.
2. Check extracted rows in Extraction Review table.
3. Test table vertical and horizontal scroll.
4. Add/remove row.
5. Add/remove column.
6. Click Generate Excel.
7. Confirm `.xlsx` file downloads.

### 6. Render Free Plan Notes

Render free backend can sleep when unused.

First request after sleep can take 30 to 60 seconds. If first upload is slow but second upload is faster, this is normal.

OCR for scanned PDFs and images is slower than text files because the backend must preprocess the file and run OCR.

### 7. Image OCR Deployment Note

Image OCR depends on Tesseract. Local Windows uses:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

Cloud Linux servers may need separate Tesseract installation. If image OCR fails on Render, check Render logs and add system package installation for Tesseract.

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
