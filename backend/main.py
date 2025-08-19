from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import random

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
    model_results = [
        {
            "model": "Swin Transformer V2",
            "confidence": random.randint(70, 90),
            "verdict": "Likely AI",
        },
        {
            "model": "EfficientNet-B7",
            "confidence": random.randint(60, 80),
            "verdict": "Uncertain",
        },
        {
            "model": "CLIP ViT-L/14",
            "confidence": random.randint(75, 95),
            "verdict": "Likely AI",
        },
    ]

    return JSONResponse(content={"results": model_results})
