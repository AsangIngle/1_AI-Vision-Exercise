# Emergency Lighting Detection from Blueprints

This project provides an automated pipeline to detect emergency lighting symbols from blueprint PDFs using YOLOv8 and OCR. The system also extracts relevant textual information near the lights and summarizes them with LLM assistance. It is served through a FastAPI web application.

---

## Features

- Detect emergency light symbols from blueprint pages
- Extract nearby text using EasyOCR
- Generate a rulebook and symbol descriptions from PDF text
- Summarize counts and descriptions of lighting symbols
- Expose two clean REST APIs (upload and result)

---

## API Endpoints

### POST /blueprints/upload

Upload a PDF and start background processing.

**Request:**

- `file`: PDF (multipart/form-data)
- `project_id` (optional): optional grouping tag

**Response:**

```json
{
  "status": "uploaded",
  "pdf_name": "E2.4.pdf",
  "message": "Processing started in background."
}
