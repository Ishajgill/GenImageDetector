"""
GenImage Detector - Swin Transformer Evaluation Script
Tracks: TPR, FNR, F1 Score, AUROC, Confusion Matrix, Recall, Precision

Usage - single dataset:
    python swin_evaluate.py \
        --checkpoint /nfs/turbo/umd-anglial/GenImageDetector/outputs/swin_full/swin_tiny_patch4_window7_224/default/ckpt_epoch_39.pth \
        --data-path /nfs/turbo/umd-anglial/GenImageDetector/raw_dataset/midjourney \
        --output-dir /nfs/turbo/umd-anglial/GenImageDetector/outputs/swin_eval_results \
        --model-name "Swin-Tiny_Midjourney"

Usage - all 8 datasets at once:
    python swin_evaluate.py \
        --checkpoint /nfs/turbo/umd-anglial/GenImageDetector/outputs/swin_full/swin_tiny_patch4_window7_224/default/ckpt_epoch_39.pth \
        --eval-all \
        --datasets-root /nfs/turbo/umd-anglial/GenImageDetector/raw_dataset \
        --output-dir /nfs/turbo/umd-anglial/GenImageDetector/outputs/swin_eval_results \
        --model-name "Swin-Tiny"
"""

import os
import sys
import argparse
import json
import torch
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from sklearn.metrics import (
    f1_score, confusion_matrix, roc_auc_score,
    precision_score, recall_score,
    ConfusionMatrixDisplay, roc_curve,
)

# Add Swin path
SWIN_PATH = '/nfs/turbo/umd-anglial/GenImageDetector/GenImage/detector_codes/Swin-Transformer-main'
sys.path.insert(0, SWIN_PATH)

from models import build_model
from config import get_config

ALL_DATASETS = ["adm", "biggan", "glide", "midjourney", "sd_v1_4", "sd_v1_5", "vqdm", "wukong"]

CONFIG_FILE = os.path.join(SWIN_PATH, 'configs/swin/swin_tiny_patch4_window7_224.yaml')

def get_args():
    parser = argparse.ArgumentParser(description="Swin Transformer GenImage Evaluation")
    parser.add_argument("--checkpoint", required=True, help="Path to .pth checkpoint file")
    parser.add_argument("--data-path", default=None, help="Path to single dataset root folder")
    parser.add_argument("--eval-all", action="store_true", help="Evaluate on all 8 datasets")
    parser.add_argument("--datasets-root", default=None, help="Root folder with all 8 dataset subfolders")
    parser.add_argument("--output-dir", required=True, help="Directory to save results")
    parser.add_argument("--model-name", default="Swin-Tiny", help="Label for this run")
    parser.add_argument("--batch-size", default=32, type=int)
    parser.add_argument("--num-workers", default=4, type=int)
    parser.add_argument("--img-size", default=224, type=int)
    # Swin config args (required by get_config)
    parser.add_argument("--cfg", default=CONFIG_FILE)
    parser.add_argument("--opts", default=None, nargs="+")
    parser.add_argument("--local_rank", default=0, type=int)
    parser.add_argument("--zip", action="store_true")
    parser.add_argument("--cache-mode", default="no")
    parser.add_argument("--pretrained", default=None)
    parser.add_argument("--resume", default=None)
    parser.add_argument("--accumulation-steps", default=1, type=int)
    parser.add_argument("--use-checkpoint", action="store_true")
    parser.add_argument("--disable_amp", action="store_true")
    parser.add_argument("--amp-opt-level", default=None)
    parser.add_argument("--output", default="/tmp/swin_output")
    parser.add_argument("--tag", default=None)
    parser.add_argument("--eval", action="store_true", default=True)
    parser.add_argument("--throughput", action="store_true")
    parser.add_argument("--fused_window_process", action="store_true")
    parser.add_argument("--fused_layernorm", action="store_true")
    parser.add_argument("--optim", default=None)
    return parser.parse_args()

def get_val_loader(data_path, img_size, batch_size, num_workers):
    val_dir = os.path.join(data_path, "val")
    if not os.path.isdir(val_dir):
        raise FileNotFoundError(f"Val directory not found: {val_dir}")
    transform = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    dataset = datasets.ImageFolder(val_dir, transform=transform)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False,
                        num_workers=num_workers, pin_memory=True)
    print(f"  Classes found: {dataset.class_to_idx}")
    print(f"  Total val images: {len(dataset)}")
    return loader, dataset.class_to_idx

def load_swin_model(checkpoint_path, config, device):
    model = build_model(config)
    print(f"  Loading checkpoint: {checkpoint_path}")
    checkpoint = torch.load(checkpoint_path, map_location="cpu")
    state_dict = checkpoint.get("model", checkpoint)
    # Handle potential key mismatches
    model_dict = model.state_dict()
    filtered = {k: v for k, v in state_dict.items() if k in model_dict and v.shape == model_dict[k].shape}
    missing = set(model_dict.keys()) - set(filtered.keys())
    if missing:
        print(f"  Note: {len(missing)} keys not loaded (expected for 2-class vs 1000-class head)")
    model_dict.update(filtered)
    model.load_state_dict(model_dict, strict=False)
    model.to(device)
    model.eval()
    print(f"  Model loaded successfully on {device}")
    return model

@torch.no_grad()
def run_inference(model, loader, class_to_idx, device):
    # Find which index corresponds to AI images
    ai_idx = class_to_idx.get("ai", 1)
    print(f"  AI class index: {ai_idx}")
    all_labels, all_preds, all_probs = [], [], []
    total = len(loader)
    for i, (images, targets) in enumerate(loader):
        if i % 50 == 0:
            print(f"  Batch {i}/{total}...")
        images = images.to(device)
        outputs = model(images)
        probs = torch.softmax(outputs, dim=1)
        # Get probability of being AI
        if probs.shape[1] >= ai_idx + 1:
            ai_probs = probs[:, ai_idx].cpu().numpy()
        else:
            ai_probs = probs[:, -1].cpu().numpy()
        preds = (ai_probs >= 0.5).astype(int)
        # Remap labels: 1 = AI, 0 = real
        remapped = (targets.numpy() == ai_idx).astype(int)
        all_labels.extend(remapped.tolist())
        all_preds.extend(preds.tolist())
        all_probs.extend(ai_probs.tolist())
    return np.array(all_labels), np.array(all_preds), np.array(all_probs)

def compute_metrics(labels, preds, probs):
    cm = confusion_matrix(labels, preds, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    fnr = fn / (tp + fn) if (tp + fn) > 0 else 0.0
    precision = precision_score(labels, preds, zero_division=0)
    recall = recall_score(labels, preds, zero_division=0)
    f1 = f1_score(labels, preds, zero_division=0)
    try:
        auroc = roc_auc_score(labels, probs)
    except ValueError:
        auroc = float("nan")
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    return {
        "accuracy": round(accuracy * 100, 2),
        "tpr": round(tpr * 100, 2),
        "fnr": round(fnr * 100, 2),
        "precision": round(precision * 100, 2),
        "recall": round(recall * 100, 2),
        "f1_score": round(f1 * 100, 2),
        "auroc": round(float(auroc), 4),
        "tp": int(tp), "tn": int(tn), "fp": int(fp), "fn": int(fn),
    }

def save_confusion_matrix(labels, preds, output_dir, title):
    cm = confusion_matrix(labels, preds, labels=[0, 1])
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Real", "AI"])
    fig, ax = plt.subplots(figsize=(6, 5))
    disp.plot(ax=ax, colorbar=False, cmap="Blues")
    ax.set_title(f"Confusion Matrix - {title}")
    path = os.path.join(output_dir, f"confusion_matrix_{title.replace(' ', '_')}.png")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  Saved confusion matrix -> {path}")

def save_roc_curve(labels, probs, auroc, output_dir, title):
    fpr, tpr_vals, _ = roc_curve(labels, probs)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(fpr, tpr_vals, label=f"AUROC = {auroc:.4f}", color="steelblue", lw=2)
    ax.plot([0, 1], [0, 1], "k--", lw=1)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title(f"ROC Curve - {title}")
    ax.legend(loc="lower right")
    path = os.path.join(output_dir, f"roc_curve_{title.replace(' ', '_')}.png")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  Saved ROC curve -> {path}")

def save_metrics_bar_chart(all_results, output_dir, model_name):
    ds_names = list(all_results.keys())
    metrics_to_plot = ["f1_score", "auroc", "precision", "recall", "accuracy"]
    colors = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2"]
    x = np.arange(len(ds_names))
    width = 0.15
    fig, ax = plt.subplots(figsize=(max(12, len(ds_names) * 2), 6))
    for i, (metric, color) in enumerate(zip(metrics_to_plot, colors)):
        vals = [all_results[ds].get(metric, 0) * (100 if metric == "auroc" else 1) for ds in ds_names]
        ax.bar(x + i * width, vals, width, label=metric.upper(), color=color)
    ax.set_xticks(x + width * 2)
    ax.set_xticklabels(ds_names, rotation=20, ha="right")
    ax.set_ylabel("Score (%)")
    ax.set_ylim(0, 115)
    ax.set_title(f"Evaluation Metrics Across All Datasets - {model_name}")
    ax.legend(loc="upper right")
    path = os.path.join(output_dir, f"metrics_comparison_{model_name.replace(' ', '_')}.png")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  Saved metrics chart -> {path}")

def save_results_json(all_results, output_dir, model_name):
    path = os.path.join(output_dir, f"results_{model_name.replace(' ', '_')}.json")
    with open(path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"  Saved JSON -> {path}")

def save_results_csv(all_results, output_dir, model_name):
    path = os.path.join(output_dir, f"results_{model_name.replace(' ', '_')}.csv")
    headers = ["dataset", "accuracy", "tpr", "fnr", "precision", "recall", "f1_score", "auroc", "tp", "tn", "fp", "fn"]
    with open(path, "w") as f:
        f.write(",".join(headers) + "\n")
        for ds, metrics in all_results.items():
            row = [ds] + [str(metrics.get(h, "")) for h in headers[1:]]
            f.write(",".join(row) + "\n")
    print(f"  Saved CSV -> {path}")

def print_summary(all_results, model_name):
    print(f"\n{'='*90}")
    print(f"  EVALUATION SUMMARY - {model_name}")
    print(f"{'='*90}")
    print(f"{'Dataset':<20} {'Acc%':>6} {'TPR%':>6} {'FNR%':>6} {'Prec%':>7} {'Rec%':>6} {'F1%':>6} {'AUROC':>7}")
    print("-" * 90)
    for ds, m in all_results.items():
        print(f"{ds:<20} {m['accuracy']:>6} {m['tpr']:>6} {m['fnr']:>6} "
              f"{m['precision']:>7} {m['recall']:>6} {m['f1_score']:>6} {m['auroc']:>7}")
    print("=" * 90)

def evaluate_single(model, data_path, args, device, output_dir, label):
    print(f"\n{'='*50}")
    print(f"  EVALUATING: {label}")
    print(f"{'='*50}")
    loader, class_to_idx = get_val_loader(data_path, args.img_size, args.batch_size, args.num_workers)
    labels, preds, probs = run_inference(model, loader, class_to_idx, device)
    metrics = compute_metrics(labels, preds, probs)
    save_confusion_matrix(labels, preds, output_dir, label)
    if not np.isnan(metrics["auroc"]):
        save_roc_curve(labels, probs, metrics["auroc"], output_dir, label)
    print(f"  Results: Acc={metrics['accuracy']}% | F1={metrics['f1_score']}% | AUROC={metrics['auroc']}")
    return metrics

def main():
    args = get_args()
    os.makedirs(args.output_dir, exist_ok=True)

    # Set up distributed (needed by Swin config)
    import torch.distributed as dist
    os.environ.setdefault("RANK", "0")
    os.environ.setdefault("WORLD_SIZE", "1")
    os.environ.setdefault("MASTER_ADDR", "localhost")
    os.environ.setdefault("MASTER_PORT", "29500")

    if not dist.is_initialized():
        dist.init_process_group(backend='nccl', init_method='env://', world_size=1, rank=0)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\nDevice: {device}")

    # Build Swin config
    config = get_config(args)
    print(f"Model: {config.MODEL.NAME}")

    # Load model
    model = load_swin_model(args.checkpoint, config, device)

    all_results = {}

    if args.eval_all:
        if not args.datasets_root:
            raise ValueError("--datasets-root required with --eval-all")
        for ds_name in ALL_DATASETS:
            ds_path = os.path.join(args.datasets_root, ds_name)
            if not os.path.isdir(ds_path):
                print(f"  WARNING: Skipping {ds_name} (folder not found)")
                continue
            try:
                metrics = evaluate_single(model, ds_path, args, device, args.output_dir, ds_name)
                all_results[ds_name] = metrics
            except Exception as e:
                print(f"  ERROR on {ds_name}: {e}")
    else:
        if not args.data_path:
            raise ValueError("--data-path required for single dataset eval")
        metrics = evaluate_single(model, args.data_path, args, device, args.output_dir, args.model_name)
        all_results[args.model_name] = metrics

    # Save all outputs
    save_results_json(all_results, args.output_dir, args.model_name)
    save_results_csv(all_results, args.output_dir, args.model_name)
    if len(all_results) > 1:
        save_metrics_bar_chart(all_results, args.output_dir, args.model_name)
    print_summary(all_results, args.model_name)
    print(f"\nAll results saved to: {args.output_dir}\n")

if __name__ == "__main__":
    main()
