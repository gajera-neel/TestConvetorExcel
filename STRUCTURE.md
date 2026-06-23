# Document To Excel AI Conversion

Modern full-stack demo app for uploading bills, invoices, receipts, PDFs, and scanned images, extracting dynamic data, editing raw rows, and downloading formatted Excel.

## Tech Stack

- Backend: Python FastAPI
- Frontend: Next.js, Tailwind CSS, TypeScript, Framer Motion
- Database: Supabase PostgreSQL through SQLAlchemy
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
→ Extraction is saved permanently to Supabase PostgreSQL
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
│   ├── config/
│   │   ├── database.py
│   │   └── supabase_client.py
│   ├── models/
│   │   └── bill.py
│   ├── routes/
│   │   ├── bills.py
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
├── .cursor/
│   └── mcp.json
├── Aptfile
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

- Supabase PostgreSQL: permanent bill/extraction records.
- `backend/uploads/`: uploaded files.
- `backend/temp/`: temporary JSON extraction sessions, kept only for current session/export compatibility and old-data migration.
- `backend/exports/`: generated Excel files.

Runtime database path:

```text
Next.js -> FastAPI -> Supabase PostgreSQL
```

Developer database path:

```text
Cursor -> MCP -> Supabase
```

MCP is only for developer operations such as schema inspection and safe queries. The app runtime does not call MCP.

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

Returns dashboard metrics from Supabase PostgreSQL, uploads by day, amount trend, bill categories, top vendors, and recent uploads.

### `GET /bills`

Returns all persisted bills from Supabase.

### `GET /bill/{id}`

Returns one bill by ID.

### `DELETE /bill/{id}`

Deletes one bill by ID.

### `POST /migrate-old-json`

Imports existing records from old `backend/temp/history.json` and temp session JSON files into Supabase PostgreSQL.

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

Required backend environment variables are read from `backend/.env` locally or Render environment variables in production:

```text
DATABASE_URL=
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
```

Never hardcode these values in Python files.

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

For Supabase persistence, Render environment variables should contain:

```text
DATABASE_URL=<your Supabase PostgreSQL connection URL>
SUPABASE_URL=<your Supabase project URL>
SUPABASE_SERVICE_ROLE_KEY=<your Supabase service role key>
```

Do not commit these values to GitHub.

Image/scan OCR on Render needs Linux system packages. The root `Aptfile` installs:

```text
tesseract-ocr
libtesseract-dev
libgl1
libglib2.0-0
```

Keep `Aptfile` in GitHub. Render reads it during deployment and installs Tesseract for image OCR.

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

This project includes `Aptfile`, so Render should install Tesseract automatically after the latest GitHub push and redeploy.

## How To Push New Updates To GitHub

After changing code locally, use these commands:

```powershell
cd D:\project
git status
git add .
git commit -m "Describe your update"
git push
```

Example:

```powershell
cd D:\project
git status
git add .
git commit -m "Fix OCR for uploaded bill images."
git push
```

What happens after `git push`:

- Vercel automatically redeploys frontend changes from `frontend/`.
- Render automatically redeploys backend changes from `backend/`, `requirements.txt`, and `Aptfile`.
- If both frontend and backend changed, both platforms redeploy.

If automatic deployment does not start:

- Vercel: open project -> `Deployments` -> `Redeploy`.
- Render: open backend service -> `Manual Deploy` -> `Deploy latest commit`.

## OCR Troubleshooting For Uploaded Bills

If an uploaded image bill shows `unknown image` and `0% confidence`, it means OCR did not read text.

Check:

1. Render latest deployment completed after the GitHub push.
2. Render logs do not show Tesseract installation errors.
3. The uploaded image is clear, upright, cropped around the bill, and not too dark.
4. Try a smaller image first.
5. Open browser console and check `[DocExcel] Extraction result`.

When OCR works, `Extraction Logs` should include detected words and the raw OCR text should appear in the browser console.

## Supabase Database Setup

Backend reads database settings only from environment variables:

```text
DATABASE_URL=
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
```

Important backend files:

- `backend/config/database.py`: SQLAlchemy `engine`, `SessionLocal`, `Base`, and `init_db()`.
- `backend/config/supabase_client.py`: Supabase service-role client helper.
- `backend/models/bill.py`: `Bill` table model.
- `backend/services/bill_service.py`: save, list, fetch, delete, and migrate bills.
- `backend/routes/bills.py`: bill APIs and old JSON migration API.

Bill model fields:

```text
id
bill_name
amount
tax
total
upload_date
raw_json
status
```

On FastAPI startup, `init_db()` creates the `bills` table if it does not exist.

### Verify Supabase Connection

Run:

```powershell
cd D:\project
python backend\scripts\verify_supabase.py
```

Expected output:

```text
Supabase connected
MCP connected
Dashboard persistence enabled
```

The script creates the table, inserts a temporary sample bill, fetches it, deletes it, and prints the status messages.

### Migrate Old JSON Data

After backend is running:

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/migrate-old-json
```

For deployed backend:

```powershell
Invoke-RestMethod -Method Post https://test-convetor-excel-backend.onrender.com/migrate-old-json
```

## Cursor Supabase MCP

MCP is for developer database operations only. Do not use MCP inside the FastAPI or Next.js runtime.

Project MCP config:

```text
.cursor/mcp.json
```

Capabilities expected from Supabase MCP:

- List tables
- Inspect schema
- Create table
- Run safe queries

The MCP config does not store app secrets. Set a Supabase personal access token in Cursor MCP settings, then restart Cursor or reload MCP servers.

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

## Dashboard Analytics Modes

The dashboard supports two Supabase-backed modes:

- `/dashboard` opens the global dashboard and calculates totals across all stored bills.
- `/dashboard?bill=<bill_id>` opens a single bill dashboard without page navigation.

Global mode shows total bills, total amount, total tax, average bill amount, upload count, amount trend, top vendors, bill categories, recent uploads, and the full uploaded bills list.

Single bill mode shows the selected bill name, upload date, vendor, extracted fields, amount, tax, table rows, summary, confidence, generated charts, and raw extraction preview.

Deleting a bill uses:

```text
DELETE /bill/{id}
```

After delete, the backend returns refreshed global dashboard data so metric cards, charts, uploaded bills, and recent uploads update immediately.

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
