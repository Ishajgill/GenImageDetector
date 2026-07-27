from typing import Any

import timm

import torch

import torch.nn as nn

from PIL import Image

from torchvision import transforms

from ml.classifiers.pytorch_base import PyTorchClassifier

MODEL_NAME = "swin_tiny_patch4_window7_224"

IMAGE_SIZE = 224

NUM_CLASSES = 2

IMAGENET_MEAN = (

    0.485,

    0.456,

    0.406,

)

IMAGENET_STD = (

    0.229,

    0.224,

    0.225,

)

class ConvertToRGB:

    """Convert incoming PIL images to three-channel RGB."""

    def __call__(self, image: Image.Image) -> Image.Image:

        return image.convert("RGB")

class SPAIModel(nn.Module):

    """

    SPAI SupCon Swin backbone with its trained linear classifier.

    Training label convention:

        class 0 = nature / real

        class 1 = AI-generated

    """

    def __init__(self):

        super().__init__()

        self.backbone = timm.create_model(

            MODEL_NAME,

            pretrained=False,

            num_classes=0,

        )

        feature_dimension = self.backbone.num_features

        if feature_dimension != 768:

            raise RuntimeError(

                "Unexpected Swin feature dimension. "

                f"Expected 768, received {feature_dimension}."

            )

        self.classifier = nn.Linear(

            feature_dimension,

            NUM_CLASSES,

        )

    def forward(self, images: torch.Tensor) -> torch.Tensor:

        features = self.backbone(images)

        logits = self.classifier(features)

        return logits

class SPAIClassifier(PyTorchClassifier):

    """

    SPAI AI-generated image detector.

    Returns a score from 0 to 100 representing the probability

    that the image is real/natural.

    """

    def __init__(

        self,

        model_path: str,

        device: str = None,

        quiet: bool = False,

    ):

        self.quiet = quiet

        super().__init__(

            model_path=model_path,

            device=device,

        )

    def get_model_architecture(self) -> nn.Module:

        return SPAIModel()

    @staticmethod

    def _remove_prefix(

        state_dict: dict[str, Any],

        prefix: str,

    ) -> dict[str, Any]:

        """

        Remove a prefix only when every state-dictionary key uses it.

        """

        if state_dict and all(

            key.startswith(prefix)

            for key in state_dict

        ):

            return {

                key[len(prefix):]: value

                for key, value in state_dict.items()

            }

        return state_dict

    def load_weights(self):

        print(

            f"[SPAI] Loading checkpoint: {self.model_path}"

        )

        try:

            checkpoint = torch.load(

                self.model_path,

                map_location=self.device,

                weights_only=False,

            )

        except TypeError:

            # Compatibility with older PyTorch versions.

            checkpoint = torch.load(

                self.model_path,

                map_location=self.device,

            )

        if not isinstance(checkpoint, dict):

            raise TypeError(

                "SPAI checkpoint must be a dictionary, "

                f"but received {type(checkpoint)}."

            )

        if "model_state_dict" not in checkpoint:

            raise KeyError(

                "SPAI checkpoint is missing "

                "'model_state_dict'. "

                f"Available keys: {list(checkpoint.keys())}"

            )

        state_dict = checkpoint["model_state_dict"]

        if not isinstance(state_dict, dict):

            raise TypeError(

                "'model_state_dict' must contain a dictionary."

            )

        # Support checkpoints saved through common wrappers.

        state_dict = self._remove_prefix(

            state_dict,

            "module.",

        )

        state_dict = self._remove_prefix(

            state_dict,

            "model.",

        )

        load_result = self.model.load_state_dict(

            state_dict,

            strict=True,

        )

        if (

            load_result.missing_keys

            or load_result.unexpected_keys

        ):

            raise RuntimeError(

                "SPAI checkpoint did not load exactly.\n"

                f"Missing keys: {load_result.missing_keys}\n"

                "Unexpected keys: "

                f"{load_result.unexpected_keys}"

            )

        saved_model_name = checkpoint.get("model_name")

        if (

            saved_model_name is not None

            and saved_model_name != MODEL_NAME

        ):

            raise RuntimeError(

                "SPAI checkpoint architecture mismatch. "

                f"Expected '{MODEL_NAME}', "

                f"checkpoint records '{saved_model_name}'."

            )

        print(

            "[SPAI] Checkpoint loaded successfully."

        )

        if not self.quiet:

            print(

                "[SPAI] "

                f"Epoch: {checkpoint.get('epoch', 'unknown')}"

            )

            print(

                "[SPAI] Validation accuracy: "

                f"{checkpoint.get('validation_accuracy', 'unknown')}"

            )

    def get_transforms(self):

        return transforms.Compose(

            [

                ConvertToRGB(),

                transforms.Resize(

                    (IMAGE_SIZE, IMAGE_SIZE)

                ),

                transforms.ToTensor(),

                transforms.Normalize(

                    mean=IMAGENET_MEAN,

                    std=IMAGENET_STD,

                ),

            ]

        )

    def postprocess(

        self,

        output: torch.Tensor,

    ) -> float:

        if output.ndim != 2 or output.shape[1] != NUM_CLASSES:

            raise RuntimeError(

                "Unexpected SPAI output shape. "

                f"Expected [batch_size, 2], got "

                f"{tuple(output.shape)}."

            )

        probabilities = torch.softmax(

            output,

            dim=1,

        )

        # SPAI training labels:

        #   index 0 = nature / real

        #   index 1 = AI-generated

        probability_real = probabilities[0, 0]

        probability_ai = probabilities[0, 1]

        confidence = round(

            probability_real.item() * 100,

            1,

        )

        if not self.quiet:

            print(

                "[SPAI Debug] "

                f"P(real)={probability_real.item():.4f}, "

                f"P(AI)={probability_ai.item():.4f}, "

                f"real confidence={confidence:.1f}%"

            )

        return confidence
