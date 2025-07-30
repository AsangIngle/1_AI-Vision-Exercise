from fastapi import FastAPI, UploadFile, File, Query
from model_utils import detect_emergency_lights, extract_rulebook_from_pdf
import os, shutil

app = FastAPI()

@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    os.makedirs("uploads", exist_ok=True)
    save_path = f"uploads/{file.filename}"
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"status": "uploaded", "file": file.filename}


@app.get("/extract/")
async def extract(pdf_name: str = Query(...)):
    pdf_path = f"uploads/{pdf_name}"
    if not os.path.exists(pdf_path):
        return {"error": "PDF not found"}

    rulebook = extract_rulebook_from_pdf(pdf_path)

    results = []
    for i in range(1, 6):  # Assuming 5 pages
        img_path = f"uploads/page_{i}.png"
        if os.path.exists(img_path):
            results += detect_emergency_lights(img_path)

    return {
        "status": "done",
        "rulebook": rulebook["rulebook"],
        "detections": results
    }
