import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
from PIL import Image
from transformers import CLIPModel as HFCLIPModel

from ml.classifiers.pytorch_base import PyTorchClassifier


CROP_SIZE = 224
# CLIP ViT-L/14 normalization (matches upstream main.py for CLIP-based archs).
CLIP_MEAN = [0.48145466, 0.4578275, 0.40821073]
CLIP_STD = [0.26862954, 0.26130258, 0.27577711]

# VIB head dimensions, vendored from oceanzhf/VIBAIGCDetect.
VIB_K = 256


class VIBNet(nn.Module):
    """Variational Information Bottleneck detector on a frozen CLIP ViT-L/14
    image encoder. Vendored from oceanzhf/VIBAIGCDetect (CVPR 2025).

    Upstream loads CLIP via the openai `clip` package and calls
    `model.encode_image`. We load the identical ViT-L/14 weights from
    HuggingFace (`openai/clip-vit-large-patch14`) and reproduce
    `encode_image` as `visual_projection(vision_model(x).pooler_output)`,
    which yields the same un-normalized 768-d projected embedding. Only the
    VIB head (fc_1 / fc_2 / fc_3 / decode) is trained and comes from the
    checkpoint; the backbone is frozen.

    Output is `((mu, std), logit)`; sigmoid(logit) is the probability that the
    image is FAKE.
    """

    def __init__(self, k: int = VIB_K):
        super().__init__()
        self.k = k

        clip_model = HFCLIPModel.from_pretrained("openai/clip-vit-large-patch14")
        # Keep only the image tower; the text tower is unused.
        self.vision_model = clip_model.vision_model
        self.visual_projection = clip_model.visual_projection
        for p in self.vision_model.parameters():
            p.requires_grad = False
        for p in self.visual_projection.parameters():
            p.requires_grad = False

        # VIB head — attribute names match the upstream checkpoint keys.
        self.fc_1 = nn.Linear(768, 1024)
        self.fc_2 = nn.Linear(1024, 1024)
        self.fc_3 = nn.Linear(1024, 2 * self.k)
        self.decode = nn.Linear(self.k, 1)
        self.relu = nn.ReLU(True)
        self.dropout = nn.Dropout(0.5)

    def encode_image(self, x: torch.Tensor) -> torch.Tensor:
        pooled = self.vision_model(pixel_values=x).pooler_output  # 1024-d
        return self.visual_projection(pooled)  # 768-d, un-normalized

    def forward(self, x: torch.Tensor):
        feat = self.encode_image(x).float()
        h = self.dropout(feat)
        h = self.relu(self.fc_1(h))
        h = self.relu(self.fc_2(h))
        statistics = self.fc_3(h)
        mu = statistics[:, : self.k]
        std = F.softplus(statistics[:, self.k :] - 5, beta=1)
        # Deterministic inference: decode the posterior mean (z = mu) instead
        # of drawing a reparameterized sample, so a given image always scores
        # the same. (Upstream samples; the mean is the standard VIB test-time
        # estimate and removes run-to-run noise.)
        logit = self.decode(mu)
        return (mu, std), logit


class VIBClassifier(PyTorchClassifier):
    """VIB-Net detector — CLIP ViT-L/14 backbone + Variational Information
    Bottleneck head. sigmoid(logit) = P(fake); we report P(real)."""

    HEAD_PREFIXES = ("fc_1", "fc_2", "fc_3", "decode")

    def __init__(self, model_path: str, device: str = None, quiet: bool = False):
        self.quiet = quiet
        super().__init__(model_path, device)

    def get_model_architecture(self) -> nn.Module:
        return VIBNet()

    def get_transforms(self):
        return transforms.Compose(
            [
                transforms.CenterCrop(CROP_SIZE),
                transforms.ToTensor(),
                transforms.Normalize(mean=CLIP_MEAN, std=CLIP_STD),
            ]
        )

    def load_weights(self):
        """Load only the VIB head from the checkpoint; the CLIP backbone is
        already initialized from HuggingFace weights."""
        print(f"[VIB] Loading checkpoint from {self.model_path}")
        ckpt = torch.load(
            self.model_path, map_location=self.device, weights_only=False
        )
        if isinstance(ckpt, dict) and "model" in ckpt and isinstance(ckpt["model"], dict):
            ckpt = ckpt["model"]
        elif isinstance(ckpt, dict) and "state_dict" in ckpt:
            ckpt = ckpt["state_dict"]

        head_state = {}
        for key, value in ckpt.items():
            nk = key.replace("module.", "")
            if nk.startswith(self.HEAD_PREFIXES):
                head_state[nk] = value

        expected = {
            n
            for n, _ in self.model.named_parameters()
            if n.startswith(self.HEAD_PREFIXES)
        }
        missing = expected - set(head_state.keys())
        if missing:
            raise RuntimeError(
                "VIB checkpoint is missing head weights: "
                f"{sorted(missing)}. Found keys: {sorted(head_state.keys())}"
            )

        # strict=False because the backbone keys live outside head_state.
        self.model.load_state_dict(head_state, strict=False)
        if not self.quiet:
            print(f"[VIB] Loaded {len(head_state)} head tensors")

    def postprocess(self, output) -> float:
        # output is ((mu, std), logit). sigmoid(logit) = P(fake).
        logit_tensor = output[1] if isinstance(output, tuple) else output
        logit = logit_tensor.view(-1)[0].item()
        prob_real = torch.sigmoid(torch.tensor(-logit)).item()
        confidence = round(prob_real * 100, 1)
        if not self.quiet:
            print(f"[VIB Debug] Logit: {logit:.4f}, Prob(real): {prob_real:.4f}")
        return confidence
