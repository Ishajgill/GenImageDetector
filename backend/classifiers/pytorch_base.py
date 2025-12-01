import torch
from PIL import Image
from abc import ABC, abstractmethod


class PyTorchClassifier(ABC):
    """
    Generic PyTorch model classifier base class.
    Subclasses should implement get_model_architecture and get_transforms.
    """

    def __init__(self, model_path: str, device: str = None):
        """
        Initialize the PyTorch classifier.

        Args:
            model_path: Path to the .pth weights file
            device: Device to run inference on ('cuda' or 'cpu'). Auto-detects if None.
        """
        self.model_path = model_path
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')

        # Load model
        self.model = self.get_model_architecture()
        self.load_weights()
        self.model.to(self.device)
        self.model.eval()

        # Get transforms
        self.transform = self.get_transforms()

    @abstractmethod
    def get_model_architecture(self) -> torch.nn.Module:
        """
        Return the model architecture.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def get_transforms(self):
        """
        Return the image transforms/preprocessing pipeline.
        Must be implemented by subclasses.
        """
        pass

    def load_weights(self):
        """
        Load model weights from .pth file.
        """
        print(f"Loading weights from {self.model_path}")
        state_dict = torch.load(self.model_path, map_location=self.device)

        # Handle different state dict formats
        if isinstance(state_dict, dict) and 'model' in state_dict:
            self.model.load_state_dict(state_dict['model'])
        else:
            self.model.load_state_dict(state_dict)

    def preprocess(self, image: Image.Image) -> torch.Tensor:
        """
        Preprocess the image for inference.

        Args:
            image: PIL Image

        Returns:
            Preprocessed tensor ready for model input
        """
        image = image.convert("RGB")
        tensor = self.transform(image)
        return tensor.unsqueeze(0)  # Add batch dimension

    @abstractmethod
    def postprocess(self, output: torch.Tensor) -> float:
        """
        Convert model output to confidence score.
        Must be implemented by subclasses.

        Args:
            output: Raw model output tensor

        Returns:
            Confidence score (0-100) that image is real
        """
        pass

    def analyze(self, image: Image.Image) -> float:
        """
        Analyze an image and return confidence that it's real.

        Args:
            image: PIL Image to analyze

        Returns:
            Confidence score (0-100) that the image is real
        """
        # Preprocess
        input_tensor = self.preprocess(image)
        input_tensor = input_tensor.to(self.device)

        # Inference
        with torch.no_grad():
            output = self.model(input_tensor)

        # Postprocess
        confidence = self.postprocess(output)
        return confidence
