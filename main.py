from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from model_utils import detect_emergency_lights, extract_rulebook_from_pdf
import fitz  # PyMuPDF
import os

app = FastAPI()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.get("/")
def root():
    return {"message": "Emergency Lighting Detection API is live."}


@app.post("/blueprints/upload")
async def upload_blueprint(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(pdf_path, "wb") as f:
        contents = await file.read()
        f.write(contents)

    # Extract rulebook
    rulebook_data = extract_rulebook_from_pdf(pdf_path)

    # Detect emergency lights
    results = []
    doc = fitz.open(pdf_path)
    for i in range(len(doc)):
        image_path = os.path.join(UPLOAD_FOLDER, f"page_{i+1}.png")
        if os.path.exists(image_path):
            detections = detect_emergency_lights(image_path)
            results.extend(detections)

    return {
        "message": "File uploaded and processed successfully.",
        "detections": results,
        "rulebook": rulebook_data["rulebook"]
    }


@app.get("/blueprints/result")
def get_result(pdf_name: str):
    pdf_path = os.path.join(UPLOAD_FOLDER, pdf_name)
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF not found.")

    rulebook_data = extract_rulebook_from_pdf(pdf_path)
    results = []

    doc = fitz.open(pdf_path)
    for i in range(len(doc)):
        image_path = os.path.join(UPLOAD_FOLDER, f"page_{i+1}.png")
        if os.path.exists(image_path):
            detections = detect_emergency_lights(image_path)
            results.extend(detections)

    return {
        "detections": results,
        "rulebook": rulebook_data["rulebook"]
    }
