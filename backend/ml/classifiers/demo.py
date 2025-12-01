"""
Placeholder classifier for UI development and demonstration purposes.

This classifier is a temporary stand-in to demonstrate the intended multi-model
ensemble functionality while additional models are being integrated. It uses
filename/path patterns to simulate the expected behavior of a second classifier
that would provide complementary analysis alongside CNNSpot.

This will be replaced with actual trained models (e.g., HuggingFace transformers,
additional CNN architectures) once they are validated and integrated into the system.
"""
import re
import random
import hashlib
from PIL import Image


class DemoClassifier:
    """
    Placeholder classifier for multi-model UI demonstration.

    Uses filename patterns to simulate expected ensemble behavior:
    - Real images: real-* prefix, midjourney/nature/* paths
    - Fake images: chatgpt-*, copilot-*, firefly-* prefixes, midjourney/ai/* paths

    NOTE: This is temporary for UI development intended to be replaced with actual
    trained classifier models once integration is complete.
    """

    def __init__(self, seed: int | str = 0):
        """
        Initialize the demo classifier.

        Args:
            seed: Optional seed value to create different "models" with varying outputs.
                  Can be an integer or string. Different seeds produce different score ranges.
        """
        # Convert string seed to integer if needed
        if isinstance(seed, str):
            self.seed = sum(ord(c) for c in seed)
        else:
            self.seed = seed

        # Patterns that suggest REAL images
        self.real_patterns = [
            r'ilsvrc',                 # ImageNet validation images
            r'real',                   # Hand-picked real images
        ]

        # Patterns that suggest FAKE/AI images
        self.fake_patterns = [
            r'midjourney',             # Midjourney generated
            r'chatgpt',                # ChatGPT generated
            r'copilot',                # Copilot generated
            r'firefly',                # Adobe Firefly generated
        ]

    def analyze(self, img: Image.Image, filename: str = "", filepath: str = "") -> float:
        """
        Analyze image using filename/path hints.

        Args:
            img: PIL Image (unused, but kept for API compatibility)
            filename: Name of the file
            filepath: Full path to the file

        Returns:
            Confidence score (0-100) that image is real
        """
        # Check filename only (not full path to avoid folder name confusion)
        filename_lower = filename.lower()

        # Check for real patterns
        is_likely_real = any(re.search(pattern, filename_lower, re.IGNORECASE)
                            for pattern in self.real_patterns)

        # Check for fake patterns
        is_likely_fake = any(re.search(pattern, filename_lower, re.IGNORECASE)
                            for pattern in self.fake_patterns)

        # Create deterministic seed from image content + classifier seed
        # Convert image to bytes and hash it for consistent randomness
        img_bytes = img.tobytes()
        img_hash = hashlib.md5(img_bytes).hexdigest()
        combined_seed = int(img_hash[:8], 16) + self.seed
        rng = random.Random(combined_seed)

        # Generate plausible-looking score based on hints
        if is_likely_real and not is_likely_fake:
            return round(rng.uniform(88.0, 97.0), 1)
        elif is_likely_fake and not is_likely_real:
            return round(rng.uniform(5.0, 25.0), 1)
        else:
            # Ambiguous: return neutral-ish score (between fake and real ranges)
            return round(rng.uniform(26.0, 87.0), 1)
