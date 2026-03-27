#!/bin/bash
#SBATCH --job-name=swin_eval
#SBATCH --account=anglial0
#SBATCH --partition=gpu-rtx6000
#SBATCH --gres=gpu:1
#SBATCH --mem=80G
#SBATCH --time=24:00:00
#SBATCH --mail-user=ishagill@umich.edu
#SBATCH --mail-type=END,FAIL
#SBATCH --output=/nfs/turbo/umd-anglial/GenImageDetector/outputs/swin_eval_%j.log

BASE=/nfs/turbo/umd-anglial/GenImageDetector
CHECKPOINT=$BASE/outputs/swin_full/swin_tiny_patch4_window7_224/default/ckpt_epoch_39.pth
EVAL_SCRIPT=$BASE/swin_evaluate.py
OUTPUT_DIR=$BASE/outputs/swin_eval_results

cd $BASE
source venv/bin/activate

RANK=0 WORLD_SIZE=1 MASTER_ADDR=localhost MASTER_PORT=29500 \
python $EVAL_SCRIPT \
  --checkpoint $CHECKPOINT \
  --eval-all \
  --datasets-root $BASE/raw_dataset \
  --output-dir $OUTPUT_DIR \
  --model-name "Swin-Tiny_Midjourney" \
  --batch-size 32 \
  --local_rank 0

echo "Evaluation complete! Results in: $OUTPUT_DIR"
