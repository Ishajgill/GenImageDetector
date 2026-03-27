#!/bin/bash
#SBATCH --job-name=vibnet_train
#SBATCH --account=anglial0
#SBATCH --partition=gpu-rtx6000
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=24:00:00
#SBATCH --output=%x-%j.out

source venv/bin/activate

cd VIBAIGCDetect

echo "Starting VIB-Net training on Midjourney..."
echo "Job ID: $SLURM_JOB_ID"
echo "Node:   $SLURMD_NODENAME"

python train.py \
    --real_path     ../raw_dataset/midjourney/train/nature \
    --fake_path     ../raw_dataset/midjourney/train/ai \
    --val_real_path ../raw_dataset/midjourney/val/nature \
    --val_fake_path ../raw_dataset/midjourney/val/ai \
    --arch          CLIP:ViT-L/14 \
    --fix_backbone \
    --num_epochs    20 \
    --batch_size    64 \
    --lr            1e-4 \
    --weight_decay  1e-4 \
    --beta          1e-3 \
    --num_workers   8 \
    --checkpoints_dir ../checkpoints/vibnet_midjourney

echo "Training complete!"
