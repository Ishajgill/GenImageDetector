import io

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image

from classifiers.base import BaseImageClassifier


ddm_classifier = BaseImageClassifier(
    "prithivMLmods/deepfake-detector-model-v1",
    {"0": "Fake", "1": "Real"},
    "Real",
)
avh_classifier = BaseImageClassifier(
    "dima806/ai_vs_human_generated_image_detection",
    {'1': "AI-generated", '0': "human"},
    "human",
)
nyuad_classifier = BaseImageClassifier(
    "NYUAD-ComNets/NYUAD_AI-generated_images_detector",
    {"0": "dalle", "1": "real", "2": "sd"},
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
async def analyze_image(file: UploadFile = File(...)):
    img_bytes = await file.read()
    try:
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {e}")

    ddm_real_confidence = ddm_classifier.analyze(img)
    avh_real_confidence = avh_classifier.analyze(img)
    nyuad_real_confidence = nyuad_classifier.analyze(img)

    real_confidences = [
        ddm_real_confidence,
        avh_real_confidence,
        nyuad_real_confidence,
    ]
    final_confidence = sum(real_confidences) / len(real_confidences)

    return JSONResponse(
        content={
            "results": [
                {
                    "model": "deepfake-detector-model-v1",
                    "confidence": ddm_real_confidence,
                },
                {
                    "model": "ai_vs_human_generated_image_detection",
                    "confidence": avh_real_confidence,
                },
                {
                    "model": "NYUAD_AI-generated_images_detector",
                    "confidence": nyuad_real_confidence,
                },
            ],
            "analysis": {
                'model': 'gid-final',
                "confidence": round(final_confidence, 1),
            },
        }
    )
