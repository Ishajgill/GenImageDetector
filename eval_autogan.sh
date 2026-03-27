#!/bin/bash
#SBATCH --job-name=autogan_eval
#SBATCH --account=anglial0
#SBATCH --partition=spgpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=180G
#SBATCH --time=6:00:00
#SBATCH --output=/nfs/turbo/umd-anglial/GenImageDetector/outputs/autogan_eval_%j.log
#SBATCH --error=/nfs/turbo/umd-anglial/GenImageDetector/outputs/autogan_eval_%j.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=cobbd@umich.edu

# Load environment
source /sw/pkgs/arc/python3.11-anaconda/2024.02-1/etc/profile.d/conda.sh
conda activate AutoGAN

# Paths
CHECKPOINT="/nfs/turbo/umd-anglial/GenImageDetector/GenImage/detector_codes/AutoGAN-master/code/model_autogan_sd_v1_4/sd_v1_4_da_fft_0_resnet/checkpoint_30.pth"
DATASETS_ROOT="/nfs/turbo/umd-anglial/GenImageDetector/raw_dataset"
OUTPUT_DIR="/nfs/turbo/umd-anglial/GenImageDetector/outputs/autogan_eval_sd_v1_4"
EVAL_SCRIPT="/nfs/turbo/umd-anglial/GenImageDetector/GenImage/detector_codes/AutoGAN-master/code/evaluate_autogan.py"

# Create output directory
mkdir -p $OUTPUT_DIR

echo "Starting AutoGAN evaluation at $(date)"
echo "Checkpoint: $CHECKPOINT"
echo "Datasets root: $DATASETS_ROOT"
echo "Output dir: $OUTPUT_DIR"

python $EVAL_SCRIPT \
    --checkpoint $CHECKPOINT \
    --eval-all \
    --datasets-root $DATASETS_ROOT \
    --output-dir $OUTPUT_DIR \
    --model-name "AutoGAN_SDv14" \
    --batch-size 16

echo "Evaluation complete at $(date)"