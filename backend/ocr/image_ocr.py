from pathlib import Path

import cv2
import pytesseract
from PIL import Image

from config import TESSERACT_EXE


if TESSERACT_EXE.exists():
    pytesseract.pytesseract.tesseract_cmd = str(TESSERACT_EXE)


def preprocess_image(file_path: Path) -> list[Image.Image]:
    image = cv2.imread(str(file_path))
    if image is None:
        return [Image.open(file_path)]

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    scale = max(2, int(1600 / max(gray.shape)))
    resized = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    denoised = cv2.fastNlMeansDenoising(resized, h=18)
    contrast = cv2.convertScaleAbs(denoised, alpha=1.7, beta=5)
    adaptive = cv2.adaptiveThreshold(
        contrast,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11,
    )
    _, otsu = cv2.threshold(contrast, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return [Image.fromarray(variant) for variant in (contrast, adaptive, otsu)]


def extract_image_text(file_path: Path) -> tuple[str, float, list[str]]:
    logs = ["Image detected", "Running local OCR with preprocessing"]
    configs = ("--oem 3 --psm 6", "--oem 3 --psm 11", "--oem 3 --psm 4")
    candidates: list[str] = []

    for image in preprocess_image(file_path):
        for config in configs:
            text = pytesseract.image_to_string(image, config=config).strip()
            if text:
                candidates.append(text)

    if not candidates:
        logs.append("No Tesseract text detected after preprocessing")
        easy_text = _try_easyocr(file_path, logs)
        if easy_text:
            return easy_text, 0.7, logs
        return "", 0.0, logs

    best = max(candidates, key=len)
    confidence = min(0.95, max(0.25, len(best.split()) / 80))
    logs.append(f"OCR completed with {len(best.split())} detected words")
    return best, round(confidence, 2), logs


def _try_easyocr(file_path: Path, logs: list[str]) -> str:
    try:
        import easyocr
    except ImportError:
        logs.append("EasyOCR not installed; skipped fallback")
        return ""

    reader = easyocr.Reader(["en"], gpu=False)
    results = reader.readtext(str(file_path), detail=0)
    text = "\n".join(results).strip()
    logs.append(f"EasyOCR fallback detected {len(text.split())} words")
    return text
