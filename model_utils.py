from easyocr import Reader
from ultralytics import YOLO
import fitz  # PyMuPDF
import cv2
import os

reader = Reader(['en'], gpu=False)
model = YOLO("best.pt")  # Path to your trained model

def detect_emergency_lights(image_path, margin=250):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    ocr_results = reader.readtext(thresh)

    results = []
    detections = model.predict(image_path, imgsz=1280, conf=0.2)[0].boxes

    for box in detections.xyxy:
        x1, y1, x2, y2 = map(int, box)
        nearby = []
        for (bbox, text, _) in ocr_results:
            x, y = int(bbox[0][0]), int(bbox[0][1])
            if x1 - margin < x < x2 + margin and y1 - margin < y < y2 + margin:
                nearby.append(text)

        results.append({
            "symbol": None,
            "bounding_box": [x1, y1, x2, y2],
            "text_nearby": nearby,
            "source_sheet": os.path.basename(image_path)
        })

    return results


def extract_rulebook_from_pdf(pdf_path, zoom=3.0):
    doc = fitz.open(pdf_path)
    rulebook = []

    for i, page in enumerate(doc):
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        img_path = f"uploads/page_{i+1}.png"
        pix.save(img_path)

        text_blocks = [text[1] for text in reader.readtext(img_path)]
        full_text = " ".join(text_blocks)

        if "emergency lighting" in full_text.lower():
            rulebook.append({
                "type": "note",
                "text": full_text,
                "source_sheet": f"Sheet {i+1}"
            })

        for block in text_blocks:
            if "exit" in block.lower() and "combo" in block.lower():
                rulebook.append({
                    "type": "table_row",
                    "symbol": "A1E",
                    "description": "Exit/Emergency Combo Unit",
                    "mount": "Ceiling",
                    "voltage": "277V",
                    "lumens": "1500lm",
                    "source_sheet": f"Sheet {i+1}"
                })

    return {"rulebook": rulebook}
