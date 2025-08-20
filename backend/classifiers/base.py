import torch
from PIL import Image
from transformers import AutoImageProcessor, SiglipForImageClassification


class BaseImageClassifier:
    def __init__(
        self, model_name: str, id2label: dict[str, str], real_key='real'
    ):
        print(model_name, id2label, real_key)
        self.model = SiglipForImageClassification.from_pretrained(model_name)
        self.processor = AutoImageProcessor.from_pretrained(model_name)
        self.id2label = id2label
        self.real_key = real_key

    def analyze(self, image: Image.Image) -> float:
        image = image.convert("RGB")
        inputs = self.processor(images=image, return_tensors="pt")

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = (
                torch.nn.functional.softmax(logits, dim=1).squeeze().tolist()
            )

        label_scores = {
            self.id2label[str(i)].lower(): probs[i] for i in range(len(probs))
        }

        real_score = label_scores.get(self.real_key) or 0
        if real_score is None:
            raise ValueError(
                f"Expected label '{self.real_key}' not found in model output."
            )

        return round(real_score * 100, 1)
