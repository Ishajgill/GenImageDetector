#!/bin/bash
#SBATCH --job-name=swin_eval
#SBATCH --account=anglial0
#SBATCH --partition=gpu_mig40
#SBATCH --gres=gpu:1
#SBATCH --mem=8G
#SBATCH --time=12:00:00
#SBATCH --mail-user=ishagill@umich.edu
#SBATCH --mail-type=END,FAIL
#SBATCH --output=/nfs/turbo/umd-anglial/GenImageDetector/outputs/eval_log_%j.log

BASE=/nfs/turbo/umd-anglial/GenImageDetector
CHECKPOINT=$BASE/outputs/swin_full/swin_tiny_patch4_window7_224/default/ckpt_epoch_39.pth
CFG=$BASE/GenImage/detector_codes/Swin-Transformer-main/configs/swin/swin_tiny_patch4_window7_224.yaml

cd $BASE
source venv/bin/activate
cd GenImage/detector_codes/Swin-Transformer-main

DATASETS=("midjourney" "sd_v1_4" "sd_v1_5" "biggan" "glide" "wukong" "vqdm" "adm")

for DATASET in "${DATASETS[@]}"; do
    echo "=========================================="
    echo "EVALUATING ON: $DATASET"
    echo "=========================================="

    RANK=0 WORLD_SIZE=1 MASTER_ADDR=localhost MASTER_PORT=29500 python main.py \
      --local_rank 0 \
      --cfg $CFG \
      --data-path $BASE/raw_dataset/$DATASET \
      --output $BASE/outputs/eval_$DATASET \
      --resume $CHECKPOINT \
      --eval

    echo "DONE: $DATASET"
    echo ""
done

echo "ALL EVALUATIONS COMPLETE"
