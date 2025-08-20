import io

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image

from analyzers.deepfake_detector_model_v1 import analyze as ddm_analyze

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

    ddm_real_confidence = ddm_analyze(img)

    real_confidences = [
        ddm_real_confidence
        # include other model results here...
    ]
    final_confidence = sum(real_confidences) / len(real_confidences)

    return JSONResponse(
        content={
            "results": [
                {
                    "model": "deepfake-detector-model-v1",
                    "confidence": ddm_real_confidence,
                },
            ],
            "analysis": {
                'model': 'gid-final',
                "confidence": round(final_confidence, 1),
            },
        }
    )
