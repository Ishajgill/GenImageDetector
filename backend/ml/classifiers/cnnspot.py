import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.models import resnet50

from ml.classifiers.pytorch_base import PyTorchClassifier


class CNNSpotClassifier(PyTorchClassifier):
    """
    CNNSpot classifier using ResNet50 architecture.
    Based on: https://github.com/peterwang512/CNNDetection
    """

    def __init__(self, model_path: str, crop_size: int = 224, device: str = None, quiet: bool = False):
        """
        Initialize CNNSpot classifier.

        Args:
            model_path: Path to the .pth weights file
            crop_size: Size to crop images to (default: 224)
            device: Device to run inference on ('cuda' or 'cpu')
            quiet: If True, suppress debug output
        """
        self.crop_size = crop_size
        self.quiet = quiet
        super().__init__(model_path, device)

    def get_model_architecture(self) -> nn.Module:
        """
        Create ResNet50 architecture with single output for binary classification.
        """
        model = resnet50(pretrained=False)
        # Replace final layer for binary classification (fake vs real)
        model.fc = nn.Linear(2048, 1)
        return model

    def get_transforms(self):
        """
        Get image preprocessing transforms for CNNSpot.
        Uses ImageNet normalization.
        """
        return transforms.Compose([
            transforms.CenterCrop(self.crop_size),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            ),
        ])

    def postprocess(self, output: torch.Tensor) -> float:
        """
        Convert model output to confidence score.

        CNNSpot outputs a single logit. Based on empirical testing on full validation:
        - Real images: HIGHER raw logits (mean ~5-8, range -8 to 38)
        - Fake images: LOWER raw logits (mean ~0-3, range -8 to 16)

        Apply skepticism bias to shift decision boundary, then sigmoid
        to convert to probability that image is REAL (since higher logits = more real).

        Args:
            output: Raw model output tensor (logits)

        Returns:
            Confidence score (0-100) that image is real
        """
        raw_logit = output.item()

        # Apply skepticism bias: subtract from raw logit to shift toward "fake"
        # Negative bias makes model more skeptical (require higher logit to classify as real)
        skepticism_bias = -4.5
        adjusted_logit = raw_logit + skepticism_bias

        # Direct sigmoid gives prob_real (since higher logits = more real)
        prob_real = torch.sigmoid(torch.tensor(adjusted_logit)).item()

        # Debug logging (unless quiet mode)
        if not self.quiet:
            print(f"[CNNSpot Debug] Raw: {raw_logit:.4f}, Adjusted: {adjusted_logit:.4f}, Prob(real): {prob_real:.4f}")

        # Convert to percentage and round
        confidence = round(prob_real * 100, 1)

        return confidence
