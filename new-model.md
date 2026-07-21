# Adding a New Detector to the Web App

This guide explains how to add a new AI-image detector (classifier) to GenImageDetector.

Most of the work is in the **backend**. The frontend builds its results list dynamically
from whatever the backend returns, so it usually needs **no changes** — the one exception is
an optional per-model display threshold.

---

## Overview

A detector is a Python class that takes a `PIL.Image` and returns a **confidence score from
0–100 that the image is REAL** (higher = more likely real, lower = more likely AI-generated).

Pipeline:

```
frontend (POST /analyze)  ->  backend/analysis/routes.py
                                  |
                                  v
                          classifier.analyze(img) -> float (0-100 = P(real))
                                  |
                                  v
            results = {"YourModel": 87.3, ...}  ->  returned as JSON
                                  |
                                  v
              frontend renders one card per key in `results`
```

Key directories:

- `backend/ml/classifiers/` — the classifier classes
- `backend/ml/models/<YourModel>/` — the trained weights (`.pth`)
- `backend/analysis/routes.py` — where classifiers are instantiated and run

---

## Step 1 — Choose a base class

There are two base classes. Pick the one that matches your model.

### A) `PyTorchClassifier` — for custom PyTorch `.pth` checkpoints

Located in `backend/ml/classifiers/pytorch_base.py`. Use this when you have your own model
architecture and a weights file. You implement four hooks:

| Method | Purpose |
| --- | --- |
| `get_model_architecture()` | Return the `nn.Module` (untrained). |
| `get_transforms()` | Return the torchvision preprocessing pipeline. |
| `postprocess(output)` | Convert the raw model output to a 0–100 **P(real)** score. |
| `load_weights()` *(optional)* | Override only if the checkpoint format is non-standard. |

The base class handles device selection, eval mode, `convert("RGB")`, batching, and
`torch.no_grad()` inference for you.

Good examples to copy from:
- `cnnspot.py` — simplest case (ResNet50, single logit).
- `npr.py` — custom architecture + custom transforms.
- `vib.py` — CLIP backbone + custom `load_weights()` that loads only the head.

### B) `BaseImageClassifier` — for HuggingFace `transformers` image classifiers

Located in `backend/ml/classifiers/base.py`. Use this when your model is a HuggingFace
`SiglipForImageClassification`-style checkpoint loaded by name. You only pass the model name
and a label map. See `AIvsHumanClassifier` and `NYUADClassifier` for examples.

---

## Step 2 — Create the classifier file

Create `backend/ml/classifiers/yourmodel.py`. Example using the PyTorch base class:

```python
import torch
import torch.nn as nn
import torchvision.transforms as transforms

from ml.classifiers.pytorch_base import PyTorchClassifier


class YourModelClassifier(PyTorchClassifier):
    """One-line description of the detector and its source/paper."""

    def __init__(self, model_path: str, device: str = None, quiet: bool = False):
        self.quiet = quiet
        super().__init__(model_path, device)

    def get_model_architecture(self) -> nn.Module:
        # Build and return your untrained architecture here.
        ...

    def get_transforms(self):
        return transforms.Compose([
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ])

    def postprocess(self, output: torch.Tensor) -> float:
        # IMPORTANT: return P(REAL) as a 0-100 number.
        # If your model outputs a logit where sigmoid(logit) = P(fake),
        # then P(real) = sigmoid(-logit).
        logit = output.view(-1)[0].item()
        prob_real = torch.sigmoid(torch.tensor(-logit)).item()
        confidence = round(prob_real * 100, 1)
        if not self.quiet:
            print(f"[YourModel Debug] Logit: {logit:.4f}, Prob(real): {prob_real:.4f}")
        return confidence
```

> **Score convention (critical):** `analyze()` must return **P(real)**, not P(fake).
> Many detectors emit a logit where `sigmoid(logit) = P(fake)`. In that case return
> `sigmoid(-logit) * 100`. Getting this backwards will invert every result for your model.

---

## Step 3 — Add the weights file

Put the trained checkpoint under its own folder:

```
backend/ml/models/YourModel/best.pth
```

Weights are large and are typically **git-ignored** (see `.gitignore`). Make sure teammates
know where to download the checkpoint from, or document it in the model folder.

---

## Step 4 — Register the classifier

Add it to the package exports in `backend/ml/classifiers/__init__.py`:

```python
from .yourmodel import YourModelClassifier

__all__ = [
    # ...existing...
    'YourModelClassifier',
]
```

---

## Step 5 — Wire it into the analyze route

In `backend/analysis/routes.py`:

1. Import it (near the other classifier imports, ~line 14):

   ```python
   from ml.classifiers.yourmodel import YourModelClassifier
   ```

2. Instantiate it once at module load (next to the other classifiers, ~line 25). It loads
   weights at startup so requests stay fast:

   ```python
   yourmodel_classifier = YourModelClassifier(
       "ml/models/YourModel/best.pth",
       quiet=True,
   )
   ```

3. Run it inside `analyze_image()` and add it to the `results` dict (~line 99). **The key you
   use here is exactly what shows up in the UI**, so name it cleanly:

   ```python
   results = {
       "CNNSpot": cnnspot_classifier.analyze(img),
       "Effort": effort_classifier.analyze(img),
       "NPR": npr_classifier.analyze(img),
       "YourModel": yourmodel_classifier.analyze(img),
   }
   ```

That's it for the core integration. The aggregate score, database persistence
(`ModelResult` rows), and history all pick up the new key automatically.

---

## Step 6 (optional) — Frontend display threshold

The frontend renders one result card per key in `results` with no code change. The only
optional tweak is a **per-model threshold** that decides the "Likely Real" vs
"Likely AI-generated" label and where the gauge flips.

Default threshold is `55`. To override it for your model, add an entry to the
`MODEL_THRESHOLDS` map. Note it currently lives in **two** places — keep them in sync:

- `frontend/src/utils.ts`
- `frontend/src/components/analyzer/Analyzer.tsx`

```ts
const MODEL_THRESHOLDS: Record<string, number> = {
  CNNSpot: 80,
  "gid-final": 50,
  YourModel: 70, // pick based on validation testing
};
```

Use the model name **exactly** as it appears as the key in the backend `results` dict.

---

## Step 7 — Test

```bash
# Backend (from backend/)
./backend_startup.sh        # or: uvicorn main:app --reload

# Frontend (from frontend/)
./frontendstartup.sh        # or: pnpm dev
```

Then:

1. Upload an image in the UI and confirm a new card appears for your model.
2. Sanity-check the score direction: a known **real** photo should score **high**, a known
   **AI-generated** image should score **low**. If it's inverted, fix the sign in
   `postprocess()` (see the score convention note in Step 2).
3. Watch the backend logs — with `quiet=False` your debug line prints the raw output and
   computed P(real), which is the fastest way to calibrate the threshold.

---

## Checklist

- [ ] `backend/ml/classifiers/yourmodel.py` created with a class returning **P(real) 0–100**
- [ ] Weights placed at `backend/ml/models/YourModel/`
- [ ] Exported from `backend/ml/classifiers/__init__.py`
- [ ] Imported, instantiated, and added to `results` in `backend/analysis/routes.py`
- [ ] (Optional) Threshold added to `MODEL_THRESHOLDS` in both frontend files
- [ ] Verified score direction on a known real and a known fake image
