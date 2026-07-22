import math
from collections.abc import Mapping

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
from PIL import Image
from transformers import CLIPModel

from ml.classifiers.pytorch_base import PyTorchClassifier


# CLIP ViT-L/14 input configuration.
IMAGE_SIZE = 224

CLIP_MEAN = [
    0.48145466,
    0.4578275,
    0.40821073,
]

CLIP_STD = [
    0.26862954,
    0.26130258,
    0.27577711,
]

# ViT-L/14 attention matrices are normally 1024 x 1024.
# r=1023 leaves a rank-1 trainable residual.
SVD_RANK = 1023

# Checkpoint names used for Effort's SVD parameters.
SVD_PARAMETER_NAMES = (
    "U_residual",
    "S_residual",
    "V_residual",
)


class SVDResidualLinear(nn.Module):
    """
    Linear layer consisting of:

        frozen low-rank main weight
        + trainable SVD residual weight

    Effective weight:

        W = W_main + U_residual @ diag(S_residual) @ V_residual
    """

    def __init__(
        self,
        in_features: int,
        out_features: int,
        r: int,
        bias: bool = True,
        init_weight: torch.Tensor | None = None,
    ):
        super().__init__()

        self.in_features = in_features
        self.out_features = out_features
        self.r = r

        self.weight_main = nn.Parameter(
            torch.empty(out_features, in_features),
            requires_grad=False,
        )

        if init_weight is not None:
            if tuple(init_weight.shape) != (
                out_features,
                in_features,
            ):
                raise ValueError(
                    "Initial weight has the wrong shape. "
                    f"Received {tuple(init_weight.shape)}, expected "
                    f"{(out_features, in_features)}."
                )

            with torch.no_grad():
                self.weight_main.copy_(init_weight)
        else:
            nn.init.kaiming_uniform_(
                self.weight_main,
                a=math.sqrt(5),
            )

        if bias:
            self.bias = nn.Parameter(
                torch.zeros(out_features)
            )
        else:
            self.register_parameter("bias", None)

        # These attributes are replaced when the original weight
        # is decomposed in replace_with_svd_residual().
        self.register_parameter("U_residual", None)
        self.register_parameter("S_residual", None)
        self.register_parameter("V_residual", None)

        # Frozen leading SVD components. They are retained for
        # checkpoint compatibility and diagnostics.
        self.register_parameter("U_r", None)
        self.register_parameter("S_r", None)
        self.register_parameter("V_r", None)

        self.register_buffer(
            "weight_original_fnorm",
            torch.tensor(0.0),
        )

        self.register_buffer(
            "weight_main_fnorm",
            torch.tensor(0.0),
        )

    def forward(
        self,
        x: torch.Tensor,
    ) -> torch.Tensor:
        weight = self.weight_main

        if (
            self.U_residual is not None
            and self.S_residual is not None
            and self.V_residual is not None
        ):
            residual_weight = (
                self.U_residual
                @ torch.diag(self.S_residual)
                @ self.V_residual
            )

            weight = weight + residual_weight

        return F.linear(
            x,
            weight,
            self.bias,
        )


def replace_with_svd_residual(
    module: nn.Module,
    r: int,
) -> nn.Module:
    """
    Replace one nn.Linear layer with SVDResidualLinear.

    The first r singular components become the frozen main weight.
    Remaining components become the residual parameters.
    """

    if not isinstance(module, nn.Linear):
        return module

    in_features = module.in_features
    out_features = module.out_features
    has_bias = module.bias is not None

    original_weight = (
        module.weight
        .detach()
        .clone()
        .float()
    )

    new_module = SVDResidualLinear(
        in_features=in_features,
        out_features=out_features,
        r=r,
        bias=has_bias,
        init_weight=original_weight,
    )

    # Preserve the original device and dtype.
    new_module = new_module.to(
        device=module.weight.device,
        dtype=module.weight.dtype,
    )

    if has_bias and module.bias is not None:
        with torch.no_grad():
            new_module.bias.copy_(
                module.bias.detach()
            )

    # Perform the decomposition in float32 for stability.
    U, S, Vh = torch.linalg.svd(
        original_weight,
        full_matrices=False,
    )

    effective_rank = min(
        r,
        S.numel(),
    )

    U_r = U[:, :effective_rank]
    S_r = S[:effective_rank]
    V_r = Vh[:effective_rank, :]

    weight_main = (
        U_r
        @ torch.diag(S_r)
        @ V_r
    )

    with torch.no_grad():
        new_module.weight_main.copy_(
            weight_main.to(
                device=new_module.weight_main.device,
                dtype=new_module.weight_main.dtype,
            )
        )

        new_module.weight_original_fnorm.copy_(
            torch.linalg.matrix_norm(
                original_weight,
                ord="fro",
            ).to(
                new_module.weight_original_fnorm.device
            )
        )

        new_module.weight_main_fnorm.copy_(
            torch.linalg.matrix_norm(
                weight_main,
                ord="fro",
            ).to(
                new_module.weight_main_fnorm.device
            )
        )

    # Store the frozen main decomposition for compatibility.
    new_module.U_r = nn.Parameter(
        U_r.to(
            device=module.weight.device,
            dtype=module.weight.dtype,
        ),
        requires_grad=False,
    )

    new_module.S_r = nn.Parameter(
        S_r.to(
            device=module.weight.device,
            dtype=module.weight.dtype,
        ),
        requires_grad=False,
    )

    new_module.V_r = nn.Parameter(
        V_r.to(
            device=module.weight.device,
            dtype=module.weight.dtype,
        ),
        requires_grad=False,
    )

    U_residual = U[:, effective_rank:]
    S_residual = S[effective_rank:]
    V_residual = Vh[effective_rank:, :]

    if S_residual.numel() > 0:
        new_module.U_residual = nn.Parameter(
            U_residual.to(
                device=module.weight.device,
                dtype=module.weight.dtype,
            ),
            requires_grad=True,
        )

        new_module.S_residual = nn.Parameter(
            S_residual.to(
                device=module.weight.device,
                dtype=module.weight.dtype,
            ),
            requires_grad=True,
        )

        new_module.V_residual = nn.Parameter(
            V_residual.to(
                device=module.weight.device,
                dtype=module.weight.dtype,
            ),
            requires_grad=True,
        )

    return new_module


def replace_linear_children(
    module: nn.Module,
    r: int,
) -> None:
    """
    Recursively replace every nn.Linear child under one module.
    """

    for child_name, child_module in list(
        module.named_children()
    ):
        if isinstance(child_module, nn.Linear):
            setattr(
                module,
                child_name,
                replace_with_svd_residual(
                    child_module,
                    r,
                ),
            )
        else:
            replace_linear_children(
                child_module,
                r,
            )


def apply_svd_residual_to_self_attn(
    model: nn.Module,
    r: int,
) -> nn.Module:
    """
    Apply SVD residual conversion to Linear layers inside
    modules named 'self_attn'.

    All parameters are frozen afterward except:
        U_residual
        S_residual
        V_residual
    """

    for child_name, child_module in list(
        model.named_children()
    ):
        if child_name == "self_attn":
            replace_linear_children(
                child_module,
                r,
            )
        else:
            apply_svd_residual_to_self_attn(
                child_module,
                r,
            )

    for parameter_name, parameter in (
        model.named_parameters()
    ):
        parameter.requires_grad = any(
            component in parameter_name
            for component in SVD_PARAMETER_NAMES
        )

    return model


class EffortModel(nn.Module):
    """
    Effort detector:

        CLIP ViT-L/14 vision backbone
        + SVD residual adaptation
        + two-class linear classifier
    """

    def __init__(self):
        super().__init__()

        print("[Effort] Loading CLIP backbone...")

        clip_model = CLIPModel.from_pretrained(
            "openai/clip-vit-large-patch14"
        )

        print("[Effort] CLIP backbone loaded")
        print("[Effort] Applying SVD residual layers...")

        vision_model = (
            apply_svd_residual_to_self_attn(
                clip_model.vision_model,
                r=SVD_RANK,
            )
        )

        print("[Effort] SVD residual layers applied")

        self.backbone = vision_model
        self.classifier = nn.Linear(
            1024,
            2,
        )

        svd_parameters = {
            name: parameter
            for name, parameter
            in self.backbone.named_parameters()
            if any(
                component in name
                for component in SVD_PARAMETER_NAMES
            )
        }

        if not svd_parameters:
            raise RuntimeError(
                "No SVD residual parameters were created in "
                "the CLIP vision backbone."
            )

        print(
            "[Effort] Model contains "
            f"{len(svd_parameters)} trainable SVD tensors"
        )

        # Print one residual rank as a diagnostic.
        for name, parameter in svd_parameters.items():
            if "S_residual" in name:
                print(
                    "[Effort] Example residual tensor: "
                    f"{name}, shape={tuple(parameter.shape)}"
                )
                break

        print("[Effort] EffortModel initialized")

    def forward(
        self,
        x: torch.Tensor,
    ) -> torch.Tensor:
        outputs = self.backbone(
            pixel_values=x
        )

        features = outputs.pooler_output
        logits = self.classifier(features)

        return logits


class EffortClassifier(PyTorchClassifier):
    """
    Effort AI-image detector.

    Output class mapping:

        class 0 = AI-generated
        class 1 = real

    analyze() returns the probability of class 1 as a
    percentage from 0 to 100.
    """

    HEAD_WEIGHT_KEYS = (
        "head.weight",
        "classifier.weight",
    )

    HEAD_BIAS_KEYS = (
        "head.bias",
        "classifier.bias",
    )

    def __init__(
        self,
        model_path: str,
        device: str | None = None,
        quiet: bool = False,
    ):
        self.quiet = quiet

        super().__init__(
            model_path,
            device,
        )

    def get_model_architecture(
        self,
    ) -> nn.Module:
        return EffortModel()

    def get_transforms(self):
        """
        Keep this preprocessing identical to the preprocessing
        used when the Effort checkpoint was trained.

        This version preserves your existing 224 x 224 resize.
        """

        return transforms.Compose(
            [
                transforms.Lambda(
                    lambda image: image.convert("RGB")
                ),
                transforms.Resize(
                    (IMAGE_SIZE, IMAGE_SIZE),
                    interpolation=(
                        transforms.InterpolationMode.BICUBIC
                    ),
                    antialias=True,
                ),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=CLIP_MEAN,
                    std=CLIP_STD,
                ),
            ]
        )

    @staticmethod
    def _remove_prefix(
        key: str,
        prefix: str,
    ) -> str:
        if key.startswith(prefix):
            return key[len(prefix):]

        return key

    @classmethod
    def _normalize_checkpoint_key(
        cls,
        key: str,
    ) -> str:
        """
        Remove common wrapper prefixes.

        Prefixes are removed only from the beginning of the key,
        unlike str.replace(), which could modify text in the
        middle of a key.
        """

        prefixes = (
            "module.",
            "model.",
            "network.",
        )

        changed = True

        while changed:
            changed = False

            for prefix in prefixes:
                updated_key = cls._remove_prefix(
                    key,
                    prefix,
                )

                if updated_key != key:
                    key = updated_key
                    changed = True

        return key

    @staticmethod
    def _unwrap_checkpoint(
        checkpoint,
    ) -> Mapping[str, torch.Tensor]:
        """
        Extract the actual state dictionary from common checkpoint
        wrapper formats.
        """

        if not isinstance(checkpoint, Mapping):
            raise RuntimeError(
                "Effort checkpoint is not a dictionary."
            )

        for wrapper_key in (
            "state_dict",
            "model",
            "model_state_dict",
        ):
            wrapped = checkpoint.get(wrapper_key)

            if isinstance(wrapped, Mapping):
                return wrapped

        return checkpoint

    @staticmethod
    def _find_first_key(
        state: Mapping[str, torch.Tensor],
        candidates: tuple[str, ...],
    ) -> str | None:
        for candidate in candidates:
            if candidate in state:
                return candidate

        return None

    def _prepare_backbone_state(
        self,
        normalized_state: Mapping[
            str,
            torch.Tensor,
        ],
    ) -> dict[str, torch.Tensor]:
        """
        Convert checkpoint backbone keys into the exact names expected
        by self.model.backbone.

        self.model.backbone is already the Hugging Face vision_model,
        so checkpoint prefixes such as:

            backbone.
            vision_model.

        must be removed before loading.
        """

        backbone_state = {}

        for original_key, value in (
            normalized_state.items()
        ):
            if original_key.startswith(
                ("head.", "classifier.")
            ):
                continue

            key = original_key

            key = self._remove_prefix(
                key,
                "backbone.",
            )

            key = self._remove_prefix(
                key,
                "vision_model.",
            )

            backbone_state[key] = value

        return backbone_state

    def _validate_svd_state(
        self,
        backbone_state: Mapping[
            str,
            torch.Tensor,
        ],
    ) -> None:
        """
        Verify that every expected Effort SVD residual tensor exists
        in the checkpoint with the correct shape.
        """

        model_state = self.model.backbone.state_dict()

        expected_svd_keys = {
            key
            for key in model_state
            if any(
                component in key
                for component in SVD_PARAMETER_NAMES
            )
        }

        checkpoint_svd_keys = {
            key
            for key in backbone_state
            if any(
                component in key
                for component in SVD_PARAMETER_NAMES
            )
        }

        matching_svd_keys = (
            expected_svd_keys
            & checkpoint_svd_keys
        )

        missing_svd_keys = sorted(
            expected_svd_keys
            - checkpoint_svd_keys
        )

        unexpected_svd_keys = sorted(
            checkpoint_svd_keys
            - expected_svd_keys
        )

        print(
            "[Effort] Expected SVD tensors: "
            f"{len(expected_svd_keys)}"
        )

        print(
            "[Effort] SVD tensors found in checkpoint: "
            f"{len(checkpoint_svd_keys)}"
        )

        print(
            "[Effort] Matching SVD tensors: "
            f"{len(matching_svd_keys)}"
        )

        if not expected_svd_keys:
            raise RuntimeError(
                "The constructed Effort model contains no "
                "SVD residual tensors."
            )

        if missing_svd_keys:
            print(
                "[Effort] Missing SVD key examples:"
            )

            for key in missing_svd_keys[:20]:
                print(f"  {key}")

            raise RuntimeError(
                "The Effort checkpoint is missing "
                f"{len(missing_svd_keys)} expected SVD "
                "residual tensors."
            )

        if unexpected_svd_keys:
            print(
                "[Effort] Unexpected checkpoint SVD "
                "key examples:"
            )

            for key in unexpected_svd_keys[:20]:
                print(f"  {key}")

            raise RuntimeError(
                "The Effort checkpoint contains "
                f"{len(unexpected_svd_keys)} SVD tensor "
                "names that do not match the model."
            )

        shape_mismatches = []

        for key in sorted(expected_svd_keys):
            checkpoint_shape = tuple(
                backbone_state[key].shape
            )

            model_shape = tuple(
                model_state[key].shape
            )

            if checkpoint_shape != model_shape:
                shape_mismatches.append(
                    (
                        key,
                        checkpoint_shape,
                        model_shape,
                    )
                )

        if shape_mismatches:
            print(
                "[Effort] SVD shape mismatches:"
            )

            for (
                key,
                checkpoint_shape,
                model_shape,
            ) in shape_mismatches[:20]:
                print(
                    f"  {key}: checkpoint="
                    f"{checkpoint_shape}, model="
                    f"{model_shape}"
                )

            raise RuntimeError(
                "The Effort checkpoint has "
                f"{len(shape_mismatches)} incompatible "
                "SVD tensor shapes. This usually means "
                "SVD_RANK does not match the training setup."
            )

        print(
            "[Effort] All expected SVD residual "
            "parameters are present and compatible"
        )

    def load_weights(self):
        print(
            "[Effort] Loading checkpoint from "
            f"{self.model_path}"
        )

        checkpoint = torch.load(
            self.model_path,
            map_location="cpu",
            weights_only=False,
        )

        print(
            "[Effort] Checkpoint loaded into memory"
        )

        raw_state = self._unwrap_checkpoint(
            checkpoint
        )

        normalized_state = {}

        for key, value in raw_state.items():
            if not isinstance(key, str):
                continue

            if not isinstance(value, torch.Tensor):
                continue

            normalized_key = (
                self._normalize_checkpoint_key(key)
            )

            normalized_state[normalized_key] = value

        if not normalized_state:
            raise RuntimeError(
                "No tensor weights were found in the "
                "Effort checkpoint."
            )

        print(
            "[Effort] Normalized checkpoint keys"
        )

        # Locate and validate the classifier head.
        head_weight_key = self._find_first_key(
            normalized_state,
            self.HEAD_WEIGHT_KEYS,
        )

        head_bias_key = self._find_first_key(
            normalized_state,
            self.HEAD_BIAS_KEYS,
        )

        if (
            head_weight_key is None
            or head_bias_key is None
        ):
            available_head_keys = sorted(
                key
                for key in normalized_state
                if (
                    "head" in key
                    or "classifier" in key
                )
            )

            raise RuntimeError(
                "Could not find the Effort classifier "
                "weights. Expected head.weight/head.bias "
                "or classifier.weight/classifier.bias. "
                "Related keys found: "
                f"{available_head_keys[:20]}"
            )

        head_state = {
            "weight": normalized_state[
                head_weight_key
            ],
            "bias": normalized_state[
                head_bias_key
            ],
        }

        expected_head_weight_shape = tuple(
            self.model.classifier.weight.shape
        )

        expected_head_bias_shape = tuple(
            self.model.classifier.bias.shape
        )

        checkpoint_head_weight_shape = tuple(
            head_state["weight"].shape
        )

        checkpoint_head_bias_shape = tuple(
            head_state["bias"].shape
        )

        if (
            checkpoint_head_weight_shape
            != expected_head_weight_shape
        ):
            raise RuntimeError(
                "Effort classifier weight shape mismatch. "
                f"Checkpoint: {checkpoint_head_weight_shape}; "
                f"model: {expected_head_weight_shape}."
            )

        if (
            checkpoint_head_bias_shape
            != expected_head_bias_shape
        ):
            raise RuntimeError(
                "Effort classifier bias shape mismatch. "
                f"Checkpoint: {checkpoint_head_bias_shape}; "
                f"model: {expected_head_bias_shape}."
            )

        print(
            "[Effort] Classifier checkpoint shapes "
            "are compatible"
        )

        backbone_state = (
            self._prepare_backbone_state(
                normalized_state
            )
        )

        # This is the critical validation step. It prevents
        # strict=False from silently ignoring the Effort-specific
        # SVD residual tensors.
        self._validate_svd_state(
            backbone_state
        )

        print(
            "[Effort] Loading backbone state_dict..."
        )

        backbone_result = (
            self.model.backbone.load_state_dict(
                backbone_state,
                strict=False,
            )
        )

        print(
            "[Effort] Backbone state_dict loaded"
        )

        # Verify again using PyTorch's actual loading result.
        missing_residual_after_load = [
            key
            for key in backbone_result.missing_keys
            if any(
                component in key
                for component in SVD_PARAMETER_NAMES
            )
        ]

        if missing_residual_after_load:
            raise RuntimeError(
                "PyTorch reported missing SVD residual "
                "parameters after loading: "
                f"{missing_residual_after_load[:20]}"
            )

        unexpected_residual_after_load = [
            key
            for key in backbone_result.unexpected_keys
            if any(
                component in key
                for component in SVD_PARAMETER_NAMES
            )
        ]

        if unexpected_residual_after_load:
            raise RuntimeError(
                "PyTorch reported unexpected SVD residual "
                "parameters after loading: "
                f"{unexpected_residual_after_load[:20]}"
            )

        print(
            "[Effort] Loading classifier head..."
        )

        self.model.classifier.load_state_dict(
            head_state,
            strict=True,
        )

        print(
            "[Effort] Classifier head loaded"
        )

        if not self.quiet:
            non_svd_missing = [
                key
                for key in backbone_result.missing_keys
                if not any(
                    component in key
                    for component in SVD_PARAMETER_NAMES
                )
            ]

            non_svd_unexpected = [
                key
                for key
                in backbone_result.unexpected_keys
                if not any(
                    component in key
                    for component in SVD_PARAMETER_NAMES
                )
            ]

            print(
                "[Effort Debug] Missing non-SVD "
                f"backbone keys ({len(non_svd_missing)}):"
            )

            for key in non_svd_missing[:20]:
                print(f"  {key}")

            print(
                "[Effort Debug] Unexpected non-SVD "
                f"checkpoint keys "
                f"({len(non_svd_unexpected)}):"
            )

            for key in non_svd_unexpected[:20]:
                print(f"  {key}")

        print(
            "[Effort] Checkpoint loading completed"
        )

    def preprocess(
        self,
        image: Image.Image,
    ) -> torch.Tensor:
        image = image.convert("RGB")
        tensor = self.transform(image)

        return tensor.unsqueeze(0)

    def postprocess(
        self,
        output: torch.Tensor,
    ) -> float:
        """
        Convert two-class logits into confidence that the
        image is real.

        Class mapping:
            class 0 = AI-generated
            class 1 = real
        """

        if output.ndim != 2:
            raise RuntimeError(
                "Effort output must have shape [batch, 2]. "
                f"Received shape {tuple(output.shape)}."
            )

        if output.shape[1] != 2:
            raise RuntimeError(
                "Effort output must contain two class logits. "
                f"Received shape {tuple(output.shape)}."
            )

        probabilities = torch.softmax(
            output,
            dim=1,
        )[0]

        probability_ai = float(
            probabilities[0].item()
        )

        probability_real = float(
            probabilities[1].item()
        )

        if not self.quiet:
            print(
                "[Effort Debug] "
                f"Prob(real): {probability_real:.4f}, "
                f"Prob(AI): {probability_ai:.4f}"
            )

        return round(
            probability_real * 100,
            1,
        )

    def analyze(
        self,
        image: Image.Image,
    ) -> float:
        """
        Analyze one PIL image and return a 0-100 confidence
        that the image is real.
        """

        self.model.eval()

        input_tensor = self.preprocess(
            image
        ).to(self.device)

        with torch.inference_mode():
            output = self.model(
                input_tensor
            )

        return self.postprocess(
            output
        )