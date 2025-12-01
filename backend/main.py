from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.routes import router as auth_router
from analysis.routes import router as analysis_router

app = FastAPI(
        title="GenImageDetector API",
        summary="AI-generated image detection and analysis service.",
        version="0.1.0"
    )

# Allow frontend to call backend for dev, adjust origins in production.
app.add_middleware(
    CORSMiddleware,
    # Vite dev server
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Include routers
app.include_router(auth_router)
app.include_router(analysis_router)
