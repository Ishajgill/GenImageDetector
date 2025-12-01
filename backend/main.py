import io
import base64

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
from pydantic import BaseModel

from classifiers.cnnspot import CNNSpotClassifier


class Base64Image(BaseModel):
    image: str


# Use only CNNSpot - trained on Midjourney, proven to work
cnnspot_classifier = CNNSpotClassifier(
    "models/CNNSpot/2025_10_22_epoch_best.pth",
    crop_size=224,
    quiet=True  # Disable debug output in production
)

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
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON or base64 image: {e}")
    else:
        # Handle file upload
        img_bytes = await file.read()
        try:
            img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image: {e}")
    
    if img is None:
        raise HTTPException(status_code=400, detail="No image provided")

    # Use CNNSpot for all predictions (trained on Midjourney dataset)
    cnnspot_real_confidence = cnnspot_classifier.analyze(img)

    return {
        "CNNSpot": cnnspot_real_confidence,
        "gid-final": cnnspot_real_confidence,
    }
