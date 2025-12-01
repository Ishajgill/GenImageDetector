import io
import base64

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
from pydantic import BaseModel

from classifiers.cnnspot import CNNSpotClassifier
from classifiers.demo import DemoClassifier


class Base64Image(BaseModel):
    image: str


# Use only CNNSpot - trained on Midjourney, proven to work
cnnspot_classifier = CNNSpotClassifier(
    "models/CNNSpot/2025_10_22_epoch_best.pth",
    crop_size=224,
    quiet=True  # Disable debug output in production
)

# Demo classifiers (for UI development)
nebula_comb_v3_classifier = DemoClassifier(seed="nebula")
open_x8100_classifier = DemoClassifier(seed="quasar")

app = FastAPI()

# Allow frontend to call backend for dev, adjust origins in production.
app.add_middleware(
    CORSMiddleware,
    # Vite dev server
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/analyze")
async def analyze_image(request: Request, file: UploadFile = File(None)):
    """
    Analyze image for AI generation. Supports both:
    - Multipart file upload (from frontend)
    - JSON with base64 image data (from batch scripts)
    """
    img = None
    filename = ""

    # Check if it's a JSON request with base64 image
    if file is None:
        try:
            body = await request.json()
            if "image" in body:
                # Decode base64 image
                img_data = body["image"]
                if img_data.startswith("data:image"):
                    # Remove data URL prefix
                    img_data = img_data.split(",", 1)[1]
                img_bytes = base64.b64decode(img_data)
                img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                filename = body.get("filename", "")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON or base64 image: {e}")
    else:
        # Handle file upload
        filename = file.filename or ""
        img_bytes = await file.read()
        try:
            img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image: {e}")

    if img is None:
        raise HTTPException(status_code=400, detail="No image provided")

    return {
        "CNNSpot": cnnspot_classifier.analyze(img),
        "Nebula_comb_v3": nebula_comb_v3_classifier.analyze(img, filename=filename),
        "open-X8100": open_x8100_classifier.analyze(img, filename=filename),
    }
