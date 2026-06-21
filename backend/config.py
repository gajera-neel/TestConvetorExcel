from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
UPLOAD_DIR = BASE_DIR / "uploads"
EXPORT_DIR = BASE_DIR / "exports"
TEMP_DIR = BASE_DIR / "temp"
HISTORY_FILE = TEMP_DIR / "history.json"

ALLOWED_EXTENSIONS = {".txt", ".png", ".jpg", ".jpeg", ".pdf"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
PDF_EXTENSIONS = {".pdf"}
TEXT_EXTENSIONS = {".txt"}
TESSERACT_EXE = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")

for directory in (UPLOAD_DIR, EXPORT_DIR, TEMP_DIR):
    directory.mkdir(exist_ok=True)
