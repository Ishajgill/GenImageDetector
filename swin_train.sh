#!/bin/bash
#SBATCH --job-name=swin_train
#SBATCH --account=anglial0
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --mem=80G
#SBATCH --time=72:00:00
#SBATCH --mail-user=ishagill@umich.edu
#SBATCH --mail-type=END,FAIL
#SBATCH --output=/nfs/turbo/umd-anglial/GenImageDetector/outputs/swin_train_%j.log

cd /nfs/turbo/umd-anglial/GenImageDetector
source venv/bin/activate
cd GenImage/detector_codes/Swin-Transformer-main

RANK=0 WORLD_SIZE=1 MASTER_ADDR=localhost MASTER_PORT=29500 python main.py \
  --local_rank 0 \
  --cfg configs/swin/swin_tiny_patch4_window7_224.yaml \
  --data-path /nfs/turbo/umd-anglial/GenImageDetector/raw_dataset/midjourney \
  --output /nfs/turbo/umd-anglial/GenImageDetector/outputs/swin_full \
  --batch-size 8 \
  --epochs 30 \
  --resume /nfs/turbo/umd-anglial/GenImageDetector/outputs/swin_full/swin_tiny_patch4_window7_224/default/ckpt_epoch_22.pth
