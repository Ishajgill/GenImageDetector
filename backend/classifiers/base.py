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


class AIvsHumanClassifier(BaseImageClassifier):
    """
    dima806/ai_vs_human_generated_image_detection

    Uses official config.json label mapping:
    - Label 0: "human" (real images)
    - Label 1: "AI-generated" (fake images)
    """
    def __init__(self, real_bias: float = 0.0):
        super().__init__(
            "dima806/ai_vs_human_generated_image_detection",
            {'0': "human", '1': "AI-generated"},  # From official config.json
            "human",
        )
        self.real_bias = real_bias

    def analyze(self, image: Image.Image) -> float:
        raw_score = super().analyze(image)
        adjusted_score = min(100.0, raw_score + self.real_bias)
        return round(adjusted_score, 1)


class NYUADClassifier(BaseImageClassifier):
    """
    NYUAD-ComNets/NYUAD_AI-generated_images_detector

    Uses official config.json label mapping:
    - Label 0: "dalle" (DALL-E generated images)
    - Label 1: "real" (real images)
    - Label 2: "sd" (Stable Diffusion generated images)
    """
    def __init__(self, real_bias: float = 0.0):
        super().__init__(
            "NYUAD-ComNets/NYUAD_AI-generated_images_detector",
            {"0": "dalle", "1": "real", "2": "sd"},  # From official config.json
        )
        self.real_bias = real_bias

    def analyze(self, image: Image.Image) -> float:
        raw_score = super().analyze(image)
        adjusted_score = min(100.0, raw_score + self.real_bias)
        return round(adjusted_score, 1)
