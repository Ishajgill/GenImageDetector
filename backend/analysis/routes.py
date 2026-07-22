"""Analysis API routes for image upload and analysis."""

import base64
import io
import os
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from huggingface_hub import hf_hub_download
from PIL import Image
from sqlalchemy.orm import Session

from analysis.models import Analysis, ModelResult
from analysis.schemas import (
    AnalysisResponse,
    HistoryMigrationRequest,
    HistoryMigrationResponse,
)
from auth.models import User
from auth.routes import get_current_user
from db.database import get_db
from ml.classifiers.cnnspot import CNNSpotClassifier
from ml.classifiers.effort import EffortClassifier
from ml.classifiers.npr import NPRClassifier
from ml.classifiers.npr_supcon import NPRSupConClassifier
from ml.classifiers.vib import VIBClassifier


router = APIRouter(tags=["Analysis"])

# Public Hugging Face repo hosting the model weights.
HF_REPO_ID = os.getenv(
    "HF_WEIGHTS_REPO",
    "danielcobb/GenImageDetector-weights",
)


def _weights(filename: str) -> str:
    """Download a model weight file and return its cached local path."""
    return hf_hub_download(
        repo_id=HF_REPO_ID,
        filename=filename,
    )


# Initialize classifiers
cnnspot_classifier = CNNSpotClassifier(
    _weights("2025_10_22_epoch_best.pth"),
    crop_size=224,
    quiet=True,
)

effort_classifier = EffortClassifier(
    _weights("effort_clip_L14_trainOn_sdv14.pth"),
    quiet=True,
)

npr_classifier = NPRClassifier(
    _weights("NPR_GenImage_sdv4.pth"),
    quiet=True,
)

npr_supcon_classifier = NPRSupConClassifier(
    model_path=(
        _weights("npr_biggan_sd14_adm_best_linear.pth")
    ),
    quiet=True,
)

vib_classifier = VIBClassifier(
    _weights("best.pth"),
    quiet=True,
)


@router.post("/analyze")
async def analyze_image(
    request: Request,
    file: UploadFile = File(None),
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Analyze an image for AI generation.

    Supports:
    - Multipart file upload from the frontend
    - JSON containing base64 image data

    If the user is authenticated, the analysis is saved to history.
    """
    img = None
    filename = ""
    image_base64 = None

    if file is None:
        try:
            body = await request.json()

            if "image" in body:
                img_data = body["image"]

                if img_data.startswith("data:image"):
                    image_base64 = img_data
                    img_data = img_data.split(",", 1)[1]
                else:
                    image_base64 = (
                        f"data:image/png;base64,{img_data}"
                    )

                img_bytes = base64.b64decode(img_data)
                img = Image.open(
                    io.BytesIO(img_bytes)
                ).convert("RGB")

                filename = body.get("filename", "")

        except Exception as error:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid JSON or base64 image: "
                    f"{error}"
                ),
            ) from error

    else:
        filename = file.filename or ""
        img_bytes = await file.read()

        try:
            img = Image.open(
                io.BytesIO(img_bytes)
            ).convert("RGB")

            buffered = io.BytesIO()
            img.save(buffered, format="PNG")

            encoded_image = base64.b64encode(
                buffered.getvalue()
            ).decode()

            image_base64 = (
                f"data:image/png;base64,{encoded_image}"
            )

        except Exception as error:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid image: {error}",
            ) from error

    if img is None:
        raise HTTPException(
            status_code=400,
            detail="No image provided",
        )

    # Run all classifiers.
    results = {
        "CNNSpot": cnnspot_classifier.analyze(img),
         "Effort": effort_classifier.analyze(img),
        #"NPR": npr_classifier.analyze(img),
        "NPR-SupCon": npr_supcon_classifier.analyze(img),
        "VIB" : vib_classifier.analyze(img),
    }



    # Calculate aggregate confidence.
    confidences = list(results.values())
    weights = [
        abs(confidence - 50)
        for confidence in confidences
    ]

    total_weight = sum(weights)

    weighted_sum = sum(
        confidence * weight
        for confidence, weight in zip(
            confidences,
            weights,
        )
    )

    aggregate_confidence = (
        round(weighted_sum / total_weight, 1)
        if total_weight > 0
        else 50.0
    )

    analysis_id = None

    if current_user:
        analysis = Analysis(
            user_id=current_user.id,
            filename=filename or "untitled",
            image_data=image_base64,
            aggregate_confidence=aggregate_confidence,
        )

        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        analysis_id = analysis.id

        for model_name, confidence in results.items():
            model_result = ModelResult(
                analysis_id=analysis.id,
                model_name=model_name,
                confidence=confidence,
            )
            db.add(model_result)

        db.commit()

    return {
        "analysis_id": analysis_id,
        "results": results,
    }


@router.get(
    "/history",
    response_model=list[AnalysisResponse],
)
async def get_history(
    current_user: Optional[User] = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    """Get the authenticated user's analysis history."""
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
        )

    analyses = (
        db.query(Analysis)
        .filter(Analysis.user_id == current_user.id)
        .order_by(Analysis.created_at.desc())
        .all()
    )

    return analyses


@router.post(
    "/migrate-history",
    response_model=HistoryMigrationResponse,
)
async def migrate_history(
    request: HistoryMigrationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Migrate anonymous analysis history to a user account."""
    migrated_count = 0
    failed_count = 0

    for item in request.items:
        try:
            analysis = Analysis(
                user_id=current_user.id,
                filename=(
                    item.filename
                    or "migrated-image"
                ),
                image_data=item.image,
                aggregate_confidence=(
                    item.aggregate_confidence
                ),
            )

            db.add(analysis)
            db.commit()
            db.refresh(analysis)

            for result in item.model_results:
                model_result = ModelResult(
                    analysis_id=analysis.id,
                    model_name=result.model_name,
                    confidence=result.confidence,
                )
                db.add(model_result)

            db.commit()
            migrated_count += 1

        except Exception as error:
            db.rollback()
            failed_count += 1

            print(
                "Failed to migrate item "
                f"{item.filename}: {error}"
            )

    return HistoryMigrationResponse(
        migrated_count=migrated_count,
        failed_count=failed_count,
        message=(
            f"Successfully migrated {migrated_count} "
            f"items, {failed_count} failed"
        ),
    )