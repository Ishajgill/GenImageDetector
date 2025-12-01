# HPC Training Guide

This guide documents practical workflows and lessons learned from training AI detection models on the University of Michigan Great Lakes HPC cluster. It's designed to help future contributors successfully train models on HPC infrastructure.

## Table of Contents

- [Quick Reference](#quick-reference)
- [Environment Setup](#environment-setup)
- [Dataset Management](#dataset-management)
- [Model Training Workflow](#model-training-workflow)
- [Common Challenges & Solutions](#common-challenges--solutions)
- [Validation & Results](#validation--results)
- [Tips for Success](#tips-for-success)

## Quick Reference

### Cluster Access

- **Dashboard**: https://greatlakes.arc-ts.umich.edu/pun/sys/dashboard/
- **SSH**: `ssh youruniqname@greatlakes.arc-ts.umich.edu`
- **VPN Required**: Use Cisco Secure Client with U-M credentials when off-campus
- **Turbo Storage**: `/nfs/turbo/umd-gid/GenImageDetector`

### GPU Request Settings (Interactive Desktop)

```
Slurm account: <username>
Partition: gpu_mig40 (GPU A100)
Number of hours: 1-24 hours
Number of cores: 2-4
Memory (GB): 1000GB
Number of GPUs: 1
```

## Environment Setup

### 1. Conda Environment Creation

Each model should have its own isolated conda environment to avoid dependency conflicts.

```bash
# Load Python module
module load python/3.13.2

# Create environment for your model
conda create -n cnnspot python=3.8
conda activate cnnspot

# Install dependencies
pip install -r requirements.txt
```

**Pro tip**: Use GitHub Copilot to help resolve dependency issues in legacy codebases. Many GenImage detector codes use outdated packages that need updating.

### 2. Common Dependency Issues

The GenImage detector codes (circa 2023) often have:

- Outdated PyTorch versions
- Incompatible numpy/scipy versions
- Missing or deprecated imports

**Solution approach**:

1. Start with the provided `requirements.txt`
2. Update packages incrementally if errors occur
3. Test imports before running full training
4. Document working versions for future reference

## Dataset Management

### Dataset Structure

```
/nfs/turbo/umd-gid/GenImageDetector/
├── raw_dataset/
│   ├── adm/
│   ├── biggan/
│   ├── glide/
│   ├── midjourney/
│   ├── stable_diffusion_v1_4/
│   ├── stable_diffusion_v1_5/
│   ├── vqdm/
│   └── wukong/
└── raw_dataset_zip/
```

Each dataset contains:

- `train/ai/` - AI-generated training images (~162K images)
- `train/nature/` - Real training images (~160K images)
- `val/ai/` - AI-generated validation images (6-8K images)
- `val/nature/` - Real validation images (6-8K images)

### Downloading Datasets

**Option 1: gdown (when it works)**

```bash
pip install gdown
gdown <google-drive-file-id>
```

**Known issue**: Google Drive has rate limits. If you see "Too many users have viewed or downloaded this file recently", you have two options:

1. Wait 24 hours and retry
2. Download locally and transfer to cluster

**Option 2: Local download + transfer**

```bash
# On local machine - download from Google Drive
# Then use WinSCP (Windows) or scp (Unix/Mac)

# Example scp command:
scp -r /path/to/dataset youruniqname@greatlakes.arc-ts.umich.edu:/nfs/turbo/umd-gid/GenImageDetector/raw_dataset_zip/
```

**Transfer speeds**: Expect ~4.7 MB/s with WinSCP, which means large datasets (30-50GB) take 1-2 hours.

### Extracting Datasets

Some archives (especially ADM) may have corruption issues. Use 7zip instead of standard unzip:

```bash
# Install 7zip on cluster
mkdir -p ~/tools && cd ~/tools
wget https://www.7-zip.org/a/7z2301-linux-x64.tar.xz
tar -xf 7z2301-linux-x64.tar.xz

# Extract with 7zip
~/tools/7zz x /nfs/turbo/umd-gid/GenImageDetector/raw_dataset_zip/adm/imagenet_ai_0508_adm.zip \
  -o/nfs/turbo/umd-gid/GenImageDetector/raw_dataset/adm
```

### Dataset Validation

Run the cleanup script to verify dataset integrity:

```bash
cd /nfs/turbo/umd-gid/GenImageDetector
python scripts/images/clean_datasets.py
```

This script:

- Counts files in each dataset split
- Identifies 0-byte corrupted files
- Removes corrupted files automatically
- Outputs results to `raw_data/scan_results.log`

## Model Training Workflow

### 1. Using Screen for Long-Running Jobs

GPU sessions are time-limited, and network disconnections can interrupt training. Use `screen` to run training in a detached process:

```bash
# Start a new screen session
screen -S cnnspot_training

# Run your training script
python train.py --dataset midjourney --epochs 50

# Detach from screen: Press Ctrl+A, then D

# Later, reattach to check progress
screen -r cnnspot_training

# List all screen sessions
screen -ls
```

**Critical**:

- Use **Ctrl+Shift+C** to copy in the terminal (not Ctrl+C)
- **Never press Ctrl+C** - this kills the training process
- Alternative: Click "Edit → Copy" in the terminal toolbar

### 2. Training Script Setup

Update dataset paths in your training script:

```python
# Example path configuration
DATA_ROOT = '/nfs/turbo/umd-gid/GenImageDetector/raw_dataset'
TRAIN_AI = f'{DATA_ROOT}/midjourney/train/ai'
TRAIN_NATURE = f'{DATA_ROOT}/midjourney/train/nature'
VAL_AI = f'{DATA_ROOT}/midjourney/val/ai'
VAL_NATURE = f'{DATA_ROOT}/midjourney/val/nature'
```

### 3. Checkpoint Management

Configure your training script to save checkpoints regularly:

```python
# Save best epoch model
if val_accuracy > best_accuracy:
    best_accuracy = val_accuracy
    torch.save(model.state_dict(), 'model_epoch_best.pth')

# Save epoch checkpoints for resuming
if epoch % 5 == 0:
    torch.save({
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'accuracy': val_accuracy
    }, f'checkpoint_epoch_{epoch}.pth')
```

**Benefits**:

- Resume training from checkpoints if GPU session expires
- Incremental training in shorter time windows
- Always have the best-performing model saved

### 4. Logging Training Progress

Enable comprehensive logging to track training:

```python
import logging

logging.basicConfig(
    filename='training_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# Log metrics each epoch
logging.info(f'Epoch {epoch}: Train Loss={train_loss:.4f}, Val Acc={val_acc:.4f}')
```

### 5. Downloading Results

After training completes, download model weights and logs:

**Windows - WinSCP**:

1. Connect to `greatlakes.arc-ts.umich.edu`
2. Navigate to your training directory
3. Download `.pth` files and `.txt` logs

**Unix/Mac - scp**:

```bash
scp youruniqname@greatlakes.arc-ts.umich.edu:/path/to/model_epoch_best.pth ./
scp youruniqname@greatlakes.arc-ts.umich.edu:/path/to/training_log.txt ./
```

### 6. Git LFS for Large Model Files

`.pth` model files are typically 100MB+ and require Git LFS:

```bash
# Install Git LFS (one-time setup)
git lfs install

# Track .pth files
git lfs track "*.pth"

# Commit .gitattributes
git add .gitattributes
git commit -m "Configure Git LFS for model weights"

# Commit model file
git add model_epoch_best.pth
git commit -m "Add trained CNNSpot model"
git push
```

## Common Challenges & Solutions

### 1. Dependency Conflicts

**Problem**: `ImportError` or `ModuleNotFoundError` when running training scripts.

**Solutions**:

- Create fresh conda environment with specific Python version
- Use GitHub Copilot to resolve import errors
- Update outdated packages (e.g., `torchvision`, `numpy`)
- Check GenImage repository issues for known fixes

### 2. Dataset Path Errors

**Problem**: Training script can't find images.

**Solutions**:

- Verify dataset extraction completed successfully
- Check paths match cluster structure: `/nfs/turbo/umd-gid/GenImageDetector/raw_dataset/<dataset_name>/`
- Update hardcoded paths in training scripts (search for `/home/`, `/data/`, etc.)
- Validate with: `ls -la /nfs/turbo/umd-gid/GenImageDetector/raw_dataset/midjourney/train/ai/ | head`

### 3. GPU Out of Memory

**Problem**: `CUDA out of memory` errors during training.

**Solutions**:

- Reduce batch size in training script
- Use gradient accumulation for effective larger batches
- Clear GPU cache: `torch.cuda.empty_cache()`
- Request more GPU memory in job submission

### 4. Training Stuck at 50% Accuracy

**Problem**: Model fails to learn, validation accuracy stays at ~50%.

**Possible causes**:

- Data loading issues (all samples from one class)
- Learning rate too high or too low
- Incorrect loss function or optimizer configuration
- Data preprocessing/normalization mismatch

**Debug steps**:

1. Print batch statistics (class distribution, pixel ranges)
2. Visualize sample inputs and augmentations
3. Try different learning rates (1e-5 to 1e-3)
4. Check model architecture matches pretrained weights (if using transfer learning)

### 5. Cluster Downtime

**Problem**: Cluster maintenance or outages interrupt training.

**Solutions**:

- Check cluster status: https://arc.umich.edu/systems-status/
- Plan training around announced maintenance windows
- Always use checkpoints to resume training
- Save logs frequently to monitor progress

## Validation & Results

### Multi-Dataset Validation

After training on one dataset (e.g., Midjourney), validate on all 8 datasets:

```bash
python validate.py --model model_epoch_best.pth --dataset adm
python validate.py --model model_epoch_best.pth --dataset biggan
python validate.py --model model_epoch_best.pth --dataset glide
# ... repeat for all datasets
```

### Metrics to Track

For each model-dataset combination, compute:

- **TPR** (True Positive Rate / Recall)
- **FNR** (False Negative Rate)
- **F1 Score**
- **AUROC** (Area Under ROC Curve)
- **Precision**
- **Confusion Matrix**

### Example Validation Script

```python
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score, confusion_matrix

# After getting predictions and ground truth
accuracy = accuracy_score(y_true, y_pred)
precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='binary')
auroc = roc_auc_score(y_true, y_scores)
cm = confusion_matrix(y_true, y_pred)

# Calculate rates
tn, fp, fn, tp = cm.ravel()
tpr = tp / (tp + fn)  # True Positive Rate
fnr = fn / (fn + tp)  # False Negative Rate

# Save results
with open(f'validation_results_{dataset}.txt', 'w') as f:
    f.write(f'Accuracy: {accuracy:.4f}\n')
    f.write(f'Precision: {precision:.4f}\n')
    f.write(f'Recall/TPR: {recall:.4f}\n')
    f.write(f'F1 Score: {f1:.4f}\n')
    f.write(f'AUROC: {auroc:.4f}\n')
    f.write(f'FNR: {fnr:.4f}\n')
    f.write(f'\nConfusion Matrix:\n{cm}\n')
```

## Tips for Success

### Before Training

1. **Test data loading** - Verify you can load a batch of images before starting training
2. **Validate environment** - Run a 1-epoch test to catch setup issues early
3. **Monitor disk space** - Check available space: `df -h /nfs/turbo/umd-gid`
4. **Review model architecture** - Understand input size, preprocessing requirements

### During Training

1. **Use screen sessions** - Always run training in detached screen
2. **Monitor periodically** - Check training logs every few hours
3. **Save frequently** - Checkpoint every 5-10 epochs minimum
4. **Track GPU usage** - Monitor with: `nvidia-smi`

### After Training

1. **Download immediately** - Transfer weights and logs to local storage
2. **Validate broadly** - Test on multiple datasets, not just training dataset
3. **Document results** - Save validation metrics for comparison
4. **Use Git LFS** - Commit model weights properly to version control
5. **Share findings** - Document what worked and what didn't for the team

### Productivity Boosters

- **GitHub Copilot**: Invaluable for debugging legacy code and updating dependencies
- **Tmux alternative**: If `screen` unavailable, use `tmux` similarly
- **Job arrays**: For validating on multiple datasets, use SLURM job arrays
- **Jupyter notebooks**: Available on cluster dashboard for interactive exploration

## Training Results Archive

The project successfully trained **CNNSpot** on the Midjourney dataset with comprehensive validation across all 8 GenImage datasets. Results are available in:

```
backend/models/CNNSpot/
├── model_epoch_best.pth           # Best performing model weights
├── training_log.txt                # Training progress and metrics
└── validation_results_*.txt        # Per-dataset validation metrics
```

### CNNSpot Training Summary

- **Training dataset**: Midjourney (162K AI + 161K real images)
- **Architecture**: ResNet-50 based with CNNSpot detection head
- **Validation**: All 8 GenImage datasets (ADM, BigGAN, GLIDE, Midjourney, SD v1.4, SD v1.5, VQDM, Wukong)
- **Integration**: Successfully deployed in production web application

## Additional Resources

- **Great Lakes Documentation**: https://arc.umich.edu/greatlakes/
- **SLURM Job Scheduling**: https://arc.umich.edu/document/slurm-user-guide/
- **Turbo Storage**: https://arc.umich.edu/document/mounting-your-turbo-volume/
- **GenImage Dataset Paper**: https://github.com/GenImage-Dataset/GenImage
- **HPC Support**: hpc-support@umich.edu

## Contributing

If you successfully train additional models, please:

1. Document your training configuration and hyperparameters
2. Share validation results across all datasets
3. Update this guide with new tips or solutions
4. Add trained model weights to `backend/models/<model_name>/`
5. Follow the model integration guide in `ONBOARDING.md`

---

**Last Updated**: December 2025
**Project**: GenImageDetector - AI-generated Image Detection System
