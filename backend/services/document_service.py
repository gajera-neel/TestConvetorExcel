from pathlib import Path

from config import IMAGE_EXTENSIONS, PDF_EXTENSIONS, TEXT_EXTENSIONS
from ocr.image_ocr import extract_image_text
from ocr.pdf_ocr import extract_pdf_text


def get_file_type(extension: str) -> str:
    ext = extension.lower()
    if ext in TEXT_EXTENSIONS:
        return "txt"
    if ext in IMAGE_EXTENSIONS:
        return "image"
    if ext in PDF_EXTENSIONS:
        return "pdf"
    return "unknown"


def detect_document_type(text: str, file_type: str) -> str:
    lowered = text.lower()
    bill_words = ("bill", "amount due", "payment", "subtotal", "tax", "gst", "total")
    invoice_words = ("invoice", "invoice no", "inv no", "gstin", "tax invoice")
    receipt_words = ("receipt", "cash", "change", "paid", "payment method")

    if any(word in lowered for word in invoice_words):
        return "invoice"
    if any(word in lowered for word in receipt_words):
        return "receipt"
    if any(word in lowered for word in bill_words):
        return "bill"
    if text.strip():
        return "normal document"
    if file_type == "image":
        return "unknown image"
    return "unknown"


def extract_document(file_path: Path, extension: str) -> dict:
    file_type = get_file_type(extension)
    logs = [f"File type detected: {file_type}"]

    if file_type == "txt":
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        confidence = 1.0 if text.strip() else 0.0
        logs.append("TXT text extracted directly")
    elif file_type == "image":
        text, confidence, ocr_logs = extract_image_text(file_path)
        logs.extend(ocr_logs)
    elif file_type == "pdf":
        text, confidence, ocr_logs = extract_pdf_text(file_path)
        logs.extend(ocr_logs)
    else:
        text = ""
        confidence = 0.0
        logs.append("Unsupported file type")

    detected_type = detect_document_type(text, file_type)
    logs.append(f"Detected document category: {detected_type}")

    return {
        "file_type": file_type,
        "detected_type": detected_type,
        "extracted_text": text,
        "confidence": round(confidence, 2),
        "logs": logs,
    }
