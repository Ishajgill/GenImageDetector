from typing import Any

import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image

from ml.classifiers.pytorch_base import PyTorchClassifier
from ml.models.NPR_SupCon.resnet import resnet50


IMAGE_SIZE = 224

CLIP_MEAN = (
    0.48145466,
    0.4578275,
    0.40821073,
)

CLIP_STD = (
    0.26862954,
    0.26130258,
    0.27577711,
)


class ConvertToRGB:
    def __call__(self, image: Image.Image) -> Image.Image:
        return image.convert("RGB")


class NPRSupConBackbone(nn.Module):
    def __init__(self):
        super().__init__()

        self.model = resnet50(
            pretrained=False,
            num_classes=1,
        )

        if hasattr(self.model, "fc1"):
            self.dim_in = self.model.fc1.in_features
        elif hasattr(self.model, "fc"):
            self.dim_in = self.model.fc.in_features
        else:
            raise AttributeError(
                "Could not locate fc1 or fc in NPR ResNet."
            )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        npr = x - self.model.interpolate(x, 0.5)

        x = self.model.conv1(npr * 2.0 / 3.0)
        x = self.model.bn1(x)
        x = self.model.relu(x)
        x = self.model.maxpool(x)

        x = self.model.layer1(x)
        x = self.model.layer2(x)

        x = self.model.avgpool(x)
        return x.view(x.size(0), -1)


class NPRSupConModel(nn.Module):
    def __init__(self):
        super().__init__()

        self.encoder = NPRSupConBackbone()
        self.classifier = nn.Linear(
            self.encoder.dim_in,
            2,
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        features = self.encoder(x)
        return self.classifier(features)


class NPRSupConClassifier(PyTorchClassifier):
    def __init__(
        self,
        model_path: str,
        device: str = None,
        quiet: bool = False,
    ):
        self.quiet = quiet
        super().__init__(model_path, device)

    def get_model_architecture(self) -> nn.Module:
        return NPRSupConModel()

    @staticmethod
    def _remove_prefix(
        state_dict: dict[str, Any],
        prefix: str,
    ) -> dict[str, Any]:
        if state_dict and all(
            key.startswith(prefix) for key in state_dict
        ):
            return {
                key[len(prefix):]: value
                for key, value in state_dict.items()
            }

        return state_dict

    def load_weights(self):
        print(
            f"[NPR-SupCon] Loading checkpoint: "
            f"{self.model_path}"
        )

        checkpoint = torch.load(
            self.model_path,
            map_location=self.device,
        )

        if "encoder" not in checkpoint:
            raise KeyError(
                "Checkpoint is missing the 'encoder' key."
            )

        if "classifier" not in checkpoint:
            raise KeyError(
                "Checkpoint is missing the 'classifier' key."
            )

        encoder_state = checkpoint["encoder"]
        classifier_state = checkpoint["classifier"]

        encoder_state = self._remove_prefix(
            encoder_state,
            "module.",
        )
        encoder_state = self._remove_prefix(
            encoder_state,
            "encoder.",
        )

        classifier_state = self._remove_prefix(
            classifier_state,
            "module.",
        )
        classifier_state = self._remove_prefix(
            classifier_state,
            "classifier.",
        )

        self.model.encoder.load_state_dict(
            encoder_state,
            strict=True,
        )

        self.model.classifier.load_state_dict(
            classifier_state,
            strict=True,
        )

        print("[NPR-SupCon] Checkpoint loaded.")

    def get_transforms(self):
        return transforms.Compose(
            [
                ConvertToRGB(),
                transforms.Resize(
                    (IMAGE_SIZE, IMAGE_SIZE)
                ),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=CLIP_MEAN,
                    std=CLIP_STD,

                ),
            ]
        )

    def postprocess(
        self,
        output: torch.Tensor,
    ) -> float:
        probabilities = torch.softmax(
            output,
            dim=1,
        )

        probability_fake = probabilities[0, 0]
        probability_real = probabilities[0, 1]

        confidence = round(
            probability_real.item() * 100,
            1,
        )

        if not self.quiet:
            print(
                "[NPR-SupCon Debug] "
                f"P(fake)={probability_fake.item():.4f}, "
                f"P(real)={probability_real.item():.4f}"
            )

        return confidence