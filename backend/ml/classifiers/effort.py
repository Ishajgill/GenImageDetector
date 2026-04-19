import math

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
from PIL import Image
from transformers import CLIPModel

from ml.classifiers.pytorch_base import PyTorchClassifier


class SVDResidualLinear(nn.Module):
    def __init__(self, in_features, out_features, r, bias=True, init_weight=None):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.r = r

        self.weight_main = nn.Parameter(
            torch.Tensor(out_features, in_features),
            requires_grad=False
        )

        if init_weight is not None:
            self.weight_main.data.copy_(init_weight)
        else:
            nn.init.kaiming_uniform_(self.weight_main, a=math.sqrt(5))

        if bias:
            self.bias = nn.Parameter(torch.Tensor(out_features))
            nn.init.zeros_(self.bias)
        else:
            self.register_parameter("bias", None)

    def forward(self, x):
        if (
            hasattr(self, "U_residual")
            and hasattr(self, "V_residual")
            and self.S_residual is not None
        ):
            residual_weight = self.U_residual @ torch.diag(self.S_residual) @ self.V_residual
            weight = self.weight_main + residual_weight
        else:
            weight = self.weight_main

        return F.linear(x, weight, self.bias)


def replace_with_svd_residual(module, r):
    if not isinstance(module, nn.Linear):
        return module

    in_features = module.in_features
    out_features = module.out_features
    bias = module.bias is not None

    new_module = SVDResidualLinear(
        in_features,
        out_features,
        r,
        bias=bias,
        init_weight=module.weight.data.clone(),
    )

    if bias and module.bias is not None:
        new_module.bias.data.copy_(module.bias.data)

    new_module.weight_original_fnorm = torch.norm(module.weight.data, p="fro")

    U, S, Vh = torch.linalg.svd(module.weight.data, full_matrices=False)
    r = min(r, len(S))

    U_r = U[:, :r]
    S_r = S[:r]
    Vh_r = Vh[:r, :]

    weight_main = U_r @ torch.diag(S_r) @ Vh_r
    new_module.weight_main_fnorm = torch.norm(weight_main.data, p="fro")
    new_module.weight_main.data.copy_(weight_main)

    U_residual = U[:, r:]
    S_residual = S[r:]
    Vh_residual = Vh[r:, :]

    if len(S_residual) > 0:
        new_module.S_residual = nn.Parameter(S_residual.clone())
        new_module.U_residual = nn.Parameter(U_residual.clone())
        new_module.V_residual = nn.Parameter(Vh_residual.clone())

        new_module.S_r = nn.Parameter(S_r.clone(), requires_grad=False)
        new_module.U_r = nn.Parameter(U_r.clone(), requires_grad=False)
        new_module.V_r = nn.Parameter(Vh_r.clone(), requires_grad=False)
    else:
        new_module.S_residual = None
        new_module.U_residual = None
        new_module.V_residual = None

        new_module.S_r = None
        new_module.U_r = None
        new_module.V_r = None

    return new_module


def apply_svd_residual_to_self_attn(model, r):
    for name, module in model.named_children():
        if "self_attn" in name:
            for sub_name, sub_module in module.named_modules():
                if isinstance(sub_module, nn.Linear):
                    parent_module = module
                    sub_module_names = sub_name.split(".")
                    for module_name in sub_module_names[:-1]:
                        parent_module = getattr(parent_module, module_name)
                    setattr(
                        parent_module,
                        sub_module_names[-1],
                        replace_with_svd_residual(sub_module, r),
                    )
        else:
            apply_svd_residual_to_self_attn(module, r)

    for param_name, param in model.named_parameters():
        if any(x in param_name for x in ["S_residual", "U_residual", "V_residual"]):
            param.requires_grad = True
        else:
            param.requires_grad = False

    return model


class EffortModel(nn.Module):
    """
    Wrap backbone + classifier head into a single nn.Module
    so it fits the repo's PyTorchClassifier pattern.
    """

    def __init__(self):
        super().__init__()

        print("[Effort] Loading CLIP backbone...")
        clip_model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
        print("[Effort] CLIP backbone loaded")

        print("[Effort] Applying SVD residual...")
        clip_model.vision_model = apply_svd_residual_to_self_attn(
            clip_model.vision_model,
            r=1023,
        )
        print("[Effort] SVD residual applied")

        self.backbone = clip_model.vision_model
        self.classifier = nn.Linear(1024, 2)

        print("[Effort] EffortModel initialized")

    def forward(self, x):
        features = self.backbone(x).pooler_output
        logits = self.classifier(features)
        return logits


class EffortClassifier(PyTorchClassifier):
    """
    Effort classifier using CLIP ViT-L/14 vision backbone + linear head.
    """

    def __init__(self, model_path: str, device: str = None, quiet: bool = False):
        self.quiet = quiet
        super().__init__(model_path, device)

    def get_model_architecture(self) -> nn.Module:
        return EffortModel()

    def get_transforms(self):
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.48145466, 0.4578275, 0.40821073],
                std=[0.26862954, 0.26130258, 0.27577711],
            ),
        ])

    def load_weights(self):
        print(f"[Effort] Loading checkpoint from {self.model_path}")
        ckpt = torch.load(self.model_path, map_location=self.device)
        print("[Effort] Checkpoint loaded into memory")

        if isinstance(ckpt, dict) and "state_dict" in ckpt:
            ckpt = ckpt["state_dict"]
            print("[Effort] Using ckpt['state_dict']")

        new_weights = {}
        for key, value in ckpt.items():
            new_key = key.replace("module.", "")
            new_key = new_key.replace("backbone.", "")
            new_weights[new_key] = value
        print("[Effort] Renamed checkpoint keys")

        print("[Effort] Loading backbone state_dict...")
        backbone_result = self.model.backbone.load_state_dict(new_weights, strict=False)
        print("[Effort] Backbone state_dict loaded")

        head_state = {}
        if "head.weight" in new_weights:
            head_state["weight"] = new_weights["head.weight"]
        if "head.bias" in new_weights:
            head_state["bias"] = new_weights["head.bias"]

        print("[Effort] Loading classifier head...")
        if len(head_state) != 2:
            raise RuntimeError(
                "Could not find classifier weights in checkpoint. "
                "Expected head.weight and head.bias."
            )

        self.model.classifier.load_state_dict(head_state, strict=True)
        print("[Effort] Classifier head loaded")

        if not self.quiet:
            print(f"[Effort Debug] Missing backbone keys: {backbone_result.missing_keys}")
            print(f"[Effort Debug] Unexpected backbone keys: {backbone_result.unexpected_keys}")

    def preprocess(self, image: Image.Image) -> torch.Tensor:
        image = image.convert("RGB")
        tensor = self.transform(image)
        return tensor.unsqueeze(0)

    def postprocess(self, output: torch.Tensor) -> float:
        """
        Convert logits to confidence that the image is REAL (0-100),
        matching the PyTorchClassifier base contract.

        Effort outputs 2-class logits:
        class 1 = real
        class 0 = AI-generated
        """
        probs = torch.softmax(output, dim=1)[0]
        prob_real = float(probs[1].item())

        if not self.quiet:
            prob_ai = float(probs[0].item())
            print(f"[Effort Debug] Prob(real): {prob_real:.4f}, Prob(AI): {prob_ai:.4f}")

        confidence = round(prob_real * 100, 1)
        return confidence

    def analyze(self, image: Image.Image) -> float:
        """
        Analyze image and return confidence (0-100) that image is REAL.
        """
        input_tensor = self.preprocess(image).to(self.device)

        with torch.no_grad():
            output = self.model(input_tensor)

        confidence = self.postprocess(output)
        return confidence