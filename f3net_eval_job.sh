#!/bin/bash
#SBATCH --job-name=f3net_eval
#SBATCH --account=anglial0
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --mem=80G
#SBATCH --time=12:00:00
#SBATCH --mail-user=ishagill@umich.edu
#SBATCH --mail-type=END,FAIL
#SBATCH --output=/nfs/turbo/umd-anglial/GenImageDetector/outputs/f3net_eval_%j.log

BASE=/nfs/turbo/umd-anglial/GenImageDetector
F3NET_DIR=$BASE/GenImage/detector_codes/F3Net-main
CHECKPOINT=$F3NET_DIR/runs/f3net_best.pth

cd $BASE
source venv/bin/activate
cd $F3NET_DIR

python eval_f3net.py \
  --ckpt $CHECKPOINT \
  --eval_all \
  --datasets_root $BASE/raw_dataset \
  --batch_size 32 \
  --num_workers 4

echo "F3Net evaluation complete!"
