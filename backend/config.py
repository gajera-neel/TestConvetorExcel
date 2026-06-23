import shutil
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
WINDOWS_TESSERACT_EXE = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
LINUX_TESSERACT_EXE = Path("/usr/bin/tesseract")
TESSERACT_EXE = (
    WINDOWS_TESSERACT_EXE
    if WINDOWS_TESSERACT_EXE.exists()
    else LINUX_TESSERACT_EXE
    if LINUX_TESSERACT_EXE.exists()
    else Path(shutil.which("tesseract") or "")
)

for directory in (UPLOAD_DIR, EXPORT_DIR, TEMP_DIR):
    directory.mkdir(exist_ok=True)
