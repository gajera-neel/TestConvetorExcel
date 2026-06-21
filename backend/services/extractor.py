from pathlib import Path

import cv2
import pdfplumber
import pytesseract
from PIL import Image


ALLOWED_EXTENSIONS = {".txt", ".png", ".jpg", ".jpeg", ".pdf"}
TESSERACT_EXE = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")

if TESSERACT_EXE.exists():
    pytesseract.pytesseract.tesseract_cmd = str(TESSERACT_EXE)


def _preprocess_image(file_path: Path) -> list[Image.Image]:
    image = cv2.imread(str(file_path))
    if image is None:
        return [Image.open(file_path)]

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    scale = max(2, int(1400 / max(gray.shape)))
    resized = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    denoised = cv2.fastNlMeansDenoising(resized, h=20)
    contrast = cv2.convertScaleAbs(denoised, alpha=1.6, beta=0)
    adaptive = cv2.adaptiveThreshold(
        contrast,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11,
    )
    _, otsu = cv2.threshold(contrast, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    variants = [contrast, adaptive, otsu]
    return [Image.fromarray(variant) for variant in variants]


def _run_image_ocr(file_path: Path) -> str:
    configs = ("--oem 3 --psm 6", "--oem 3 --psm 11", "--oem 3 --psm 4")
    candidates = []

    for image in _preprocess_image(file_path):
        for config in configs:
            text = pytesseract.image_to_string(image, config=config).strip()
            if text:
                candidates.append(text)

    if not candidates:
        original = Image.open(file_path)
        return pytesseract.image_to_string(original).strip()

    return max(candidates, key=len)


def get_file_type(extension: str) -> str:
    ext = extension.lower()
    if ext == ".txt":
        return "text"
    if ext in {".png", ".jpg", ".jpeg"}:
        return "image"
    if ext == ".pdf":
        return "pdf"
    return "unknown"


def extract_text(file_path: Path, extension: str) -> str:
    ext = extension.lower()

    if ext == ".txt":
        return file_path.read_text(encoding="utf-8", errors="ignore")

    if ext in {".png", ".jpg", ".jpeg"}:
        return _run_image_ocr(file_path)

    if ext == ".pdf":
        text_parts = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n\n".join(text_parts).strip()

    return ""
