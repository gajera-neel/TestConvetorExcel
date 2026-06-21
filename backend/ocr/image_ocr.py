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
    max_side = max(gray.shape)
    target_side = 1800
    scale = target_side / max_side if max_side > target_side else min(2.0, max(1.0, target_side / max_side))
    resized = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    denoised = cv2.fastNlMeansDenoising(resized, h=12)
    contrast = cv2.convertScaleAbs(denoised, alpha=1.7, beta=5)
    adaptive = cv2.adaptiveThreshold(
        contrast,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11,
    )

    return [Image.fromarray(variant) for variant in (adaptive, contrast)]


def extract_image_text(file_path: Path) -> tuple[str, float, list[str]]:
    logs = ["Image detected", "Running local OCR with preprocessing"]
    configs = ("--oem 3 --psm 6", "--oem 3 --psm 11")
    candidates: list[str] = []

    for image in preprocess_image(file_path):
        for config in configs:
            try:
                text = pytesseract.image_to_string(image, config=config, timeout=25).strip()
            except RuntimeError:
                logs.append("One OCR pass timed out and was skipped")
                continue
            if text:
                candidates.append(text)
                if len(text.split()) >= 12:
                    break
        if candidates and len(max(candidates, key=len).split()) >= 12:
            break

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
