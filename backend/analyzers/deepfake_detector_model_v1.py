import torch
from transformers import AutoImageProcessor, SiglipForImageClassification
from PIL import Image

model_name = "prithivMLmods/deepfake-detector-model-v1"
model = SiglipForImageClassification.from_pretrained(model_name)
processor = AutoImageProcessor.from_pretrained(model_name)

id_labels = {"0": "fake", "1": "real"}


def analyze(image):
    image = image.convert("RGB")
    inputs = processor(images=image, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = torch.nn.functional.softmax(logits, dim=1).squeeze().tolist()

    prediction = {
        id_labels[str(i)]: round(probs[i], 3) for i in range(len(probs))
    }

    real_confidence = round(prediction["real"] * 100, 1)

    return real_confidence
