from pathlib import Path

import pdfplumber

from ocr.image_ocr import extract_image_text


def _render_pdf_pages(file_path: Path) -> list[Path]:
    try:
        import pypdfium2 as pdfium
    except ImportError:
        return []

    rendered_paths = []
    pdf = pdfium.PdfDocument(str(file_path))
    for index in range(len(pdf)):
        page = pdf[index]
        bitmap = page.render(scale=2).to_pil()
        image_path = file_path.with_name(f"{file_path.stem}_page_{index + 1}.png")
        bitmap.save(image_path)
        rendered_paths.append(image_path)
    return rendered_paths


def extract_pdf_text(file_path: Path) -> tuple[str, float, list[str]]:
    logs = ["PDF detected", "Trying pdfplumber text extraction"]
    text_parts = []

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

    extracted = "\n\n".join(text_parts).strip()
    if extracted:
        logs.append("PDF text layer found")
        return extracted, 0.9, logs

    logs.append("No PDF text layer found, using OCR fallback")
    ocr_text = []
    confidences = []
    rendered_paths = _render_pdf_pages(file_path)

    for image_path in rendered_paths:
        page_text, confidence, page_logs = extract_image_text(image_path)
        ocr_text.append(page_text)
        confidences.append(confidence)
        logs.extend(page_logs)
        image_path.unlink(missing_ok=True)

    final_text = "\n\n".join(part for part in ocr_text if part).strip()
    confidence = sum(confidences) / len(confidences) if confidences else 0.0
    return final_text, round(confidence, 2), logs
