from typing import Any

import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image

from ml.classifiers.effort import CLIP_MEAN, CLIP_STD, IMAGE_SIZE, SVD_PARAMETER_NAMES, EffortModel
from ml.classifiers.pytorch_base import PyTorchClassifier


# Prefix used by the raw Phase 1 SupCon-pretraining checkpoint (last.pth),
# whose top-level 'model' dict nests the backbone under 'encoder.model.'
# and the contrastive projection head under 'head.'.
PHASE1_ENCODER_PREFIX = "encoder.model."

# Prefix used by a combined Phase 2 (linear-probe) checkpoint's 'encoder'
# sub-dict, which mirrors the same wrapper nesting as Phase 1
# (i.e. 'encoder' -> 'model.<backbone keys>').
PHASE2_ENCODER_SUBPREFIX = "model."

CLASSIFIER_STATE_KEYS = ("classifier", "head", "fc", "linear")


def _strip_prefix(state_dict: dict[str, Any], prefix: str) -> dict[str, Any]:
    if state_dict and all(key.startswith(prefix) for key in state_dict):
        return {key[len(prefix):]: value for key, value in state_dict.items()}
    return state_dict


def _diagnostic_buffers_only(keys: list[str]) -> bool:
    return all(key.endswith(("weight_original_fnorm", "weight_main_fnorm")) for key in keys)


class EffortSupConClassifier(PyTorchClassifier):
    """
    Effort + SupCon variant.

    Architecture is identical to the baseline Effort model (CLIP ViT-L/14 +
    SVD-residual adapters, r=1023, 2-class linear head) - only the weights
    differ. The backbone was pretrained with SupCon (supervised contrastive
    learning) on biggan_sd14_adm_combined_v2, then a linear classifier head
    was trained on top in a separate probing stage.

    Two checkpoints are involved:
      - encoder_path: Phase 1 SupCon-pretrained encoder (last.pth). Its
        top-level 'model' dict has backbone keys nested under
        'encoder.model.' and a contrastive projection head under 'head.'
        (unused for inference - it's the 128-dim SupCon projection head,
        not a classifier).
      - linear_head_path: Phase 2 linear-probe checkpoint. This may either
        already contain the full backbone state (top-level 'encoder' key)
        alongside the trained 'classifier' head, or it may contain only the
        classifier head, in which case the backbone falls back to
        encoder_path.

    Output class mapping matches EffortClassifier: class 0 = AI-generated,
    class 1 = real.
    """

    def __init__(
        self,
        encoder_path: str,
        linear_head_path: str,
        device: str | None = None,
        quiet: bool = False,
    ):
        self.encoder_path = encoder_path
        self.linear_head_path = linear_head_path
        self.quiet = quiet

        super().__init__(encoder_path, device)

    def get_model_architecture(self) -> nn.Module:
        return EffortModel()

    def get_transforms(self):
        return transforms.Compose(
            [
                transforms.Lambda(lambda image: image.convert("RGB")),
                transforms.Resize(
                    (IMAGE_SIZE, IMAGE_SIZE),
                    interpolation=transforms.InterpolationMode.BICUBIC,
                    antialias=True,
                ),
                transforms.ToTensor(),
                transforms.Normalize(mean=CLIP_MEAN, std=CLIP_STD),
            ]
        )

    def _load_backbone_state_dict(self, backbone_state: dict[str, Any], source: str) -> None:
        result = self.model.backbone.load_state_dict(backbone_state, strict=False)

        if result.unexpected_keys:
            raise RuntimeError(
                f"[Effort-SupCon] Unexpected keys loading backbone from {source}: "
                f"{result.unexpected_keys[:20]}"
            )

        if not _diagnostic_buffers_only(result.missing_keys):
            real_missing = [
                key for key in result.missing_keys
                if not key.endswith(("weight_original_fnorm", "weight_main_fnorm"))
            ]
            raise RuntimeError(
                f"[Effort-SupCon] Backbone checkpoint from {source} is missing "
                f"real weights (not just diagnostic fnorm buffers): {real_missing[:20]}"
            )

        missing_svd = [
            key for key in result.missing_keys
            if any(component in key for component in SVD_PARAMETER_NAMES)
        ]

        if missing_svd:
            raise RuntimeError(
                f"[Effort-SupCon] Backbone checkpoint from {source} is missing "
                f"SVD residual tensors: {missing_svd[:20]}"
            )

        print(
            f"[Effort-SupCon] Backbone loaded from {source}: "
            f"{len(backbone_state)} keys matched, "
            f"{len(result.missing_keys)} diagnostic-only buffers unset."
        )

    def _load_phase1_encoder(self) -> None:
        print(f"[Effort-SupCon] Loading Phase 1 SupCon encoder checkpoint: {self.encoder_path}")

        checkpoint = torch.load(self.encoder_path, map_location="cpu", weights_only=False)

        if "model" not in checkpoint:
            raise KeyError("[Effort-SupCon] Phase 1 checkpoint is missing the 'model' key.")

        model_state = checkpoint["model"]

        backbone_state = {
            key[len(PHASE1_ENCODER_PREFIX):]: value
            for key, value in model_state.items()
            if key.startswith(PHASE1_ENCODER_PREFIX)
        }

        if not backbone_state:
            raise RuntimeError(
                "[Effort-SupCon] No keys with prefix "
                f"'{PHASE1_ENCODER_PREFIX}' found in Phase 1 checkpoint."
            )

        self._load_backbone_state_dict(backbone_state, source="Phase 1 (last.pth)")

    def _extract_phase2_encoder_state(self, checkpoint: dict[str, Any]) -> dict[str, Any] | None:
        encoder_state = checkpoint.get("encoder")

        if not isinstance(encoder_state, dict) or not encoder_state:
            return None

        encoder_state = _strip_prefix(encoder_state, "module.")
        encoder_state = _strip_prefix(encoder_state, PHASE2_ENCODER_SUBPREFIX)

        return encoder_state

    def _extract_phase2_classifier_state(self, checkpoint: dict[str, Any]) -> dict[str, Any]:
        for key in CLASSIFIER_STATE_KEYS:
            candidate = checkpoint.get(key)

            if isinstance(candidate, dict) and {"weight", "bias"} <= candidate.keys():
                return _strip_prefix(candidate, "module.")

        if isinstance(checkpoint, dict) and {"weight", "bias"} <= checkpoint.keys():
            return checkpoint

        raise RuntimeError(
            "[Effort-SupCon] Could not locate the linear classifier weights in "
            f"the Phase 2 checkpoint. Top-level keys found: {list(checkpoint.keys())}"
        )

    def _load_phase2_classifier(self, classifier_state: dict[str, Any]) -> None:
        expected_weight_shape = tuple(self.model.classifier.weight.shape)
        expected_bias_shape = tuple(self.model.classifier.bias.shape)

        checkpoint_weight_shape = tuple(classifier_state["weight"].shape)
        checkpoint_bias_shape = tuple(classifier_state["bias"].shape)

        if checkpoint_weight_shape != expected_weight_shape or checkpoint_bias_shape != expected_bias_shape:
            raise RuntimeError(
                "[Effort-SupCon] Linear-probe classifier shape mismatch. "
                f"Checkpoint: weight={checkpoint_weight_shape}, bias={checkpoint_bias_shape}; "
                f"model: weight={expected_weight_shape}, bias={expected_bias_shape}."
            )

        self.model.classifier.load_state_dict(
            {"weight": classifier_state["weight"], "bias": classifier_state["bias"]},
            strict=True,
        )

        print("[Effort-SupCon] Linear-probe classifier head loaded.")

    def load_weights(self):
        print(f"[Effort-SupCon] Loading Phase 2 linear-probe checkpoint: {self.linear_head_path}")

        phase2_checkpoint = torch.load(self.linear_head_path, map_location="cpu", weights_only=False)

        if not isinstance(phase2_checkpoint, dict):
            raise RuntimeError("[Effort-SupCon] Phase 2 checkpoint is not a dictionary.")

        classifier_state = self._extract_phase2_classifier_state(phase2_checkpoint)
        self._load_phase2_classifier(classifier_state)

        phase2_encoder_state = self._extract_phase2_encoder_state(phase2_checkpoint)

        if phase2_encoder_state:
            self._load_backbone_state_dict(phase2_encoder_state, source="Phase 2 (combined checkpoint)")
        else:
            self._load_phase1_encoder()

    def postprocess(self, output: torch.Tensor) -> float:
        """
        Convert two-class logits into confidence that the image is real.

        Class mapping (matches EffortClassifier):
            class 0 = AI-generated
            class 1 = real
        """
        if output.ndim != 2 or output.shape[1] != 2:
            raise RuntimeError(
                "[Effort-SupCon] Output must have shape [batch, 2]. "
                f"Received shape {tuple(output.shape)}."
            )

        probabilities = torch.softmax(output, dim=1)[0]

        probability_ai = float(probabilities[0].item())
        probability_real = float(probabilities[1].item())

        if not self.quiet:
            print(
                "[Effort-SupCon Debug] "
                f"Prob(real): {probability_real:.4f}, Prob(AI): {probability_ai:.4f}"
            )

        return round(probability_real * 100, 1)

    def analyze(self, image: Image.Image) -> float:
        self.model.eval()

        input_tensor = self.preprocess(image).to(self.device)

        with torch.inference_mode():
            output = self.model(input_tensor)

        return self.postprocess(output)
