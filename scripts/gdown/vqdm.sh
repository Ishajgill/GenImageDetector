#!/bin/bash

BASE_DIR="/nfs/turbo/umd-anglial/GenImageDetector/raw_dataset_zip"
mkdir -p "$BASE_DIR"
cd "$BASE_DIR" || exit

VQDM_DIR="$BASE_DIR/vqdm"
mkdir -p "$VQDM_DIR"
cd "$VQDM_DIR" || exit

links=(
  "https://drive.google.com/file/d/12hRuzHQ-eAbrJeGS01n1iYNHYYl0A0LV/view?usp=drive_link"
  "https://drive.google.com/file/d/1y_fjkvzTWHXAbzIurRmdQ_rU54Dj0B45/view?usp=drive_link"
  "https://drive.google.com/file/d/15pVNrnfoFebBjM4utOW1UuzyKVBsUxjC/view?usp=drive_link"
  "https://drive.google.com/file/d/1xKpZOC9Rbe0EQMH6HxhmqfZeI0y13Opq/view?usp=drive_link"
  "https://drive.google.com/file/d/1Yjsi-auGqvOZV3r6hfcrgoHbWVLag6jN/view?usp=drive_link"
  "https://drive.google.com/file/d/1tm0ierEBLH18ZqviTy8Ds86Fu1lTrIrr/view?usp=drive_link"
  "https://drive.google.com/file/d/1ZT_l-jRj-1GyXnuaBxGCZKzjk0TCZDqV/view?usp=drive_link"
  "https://drive.google.com/file/d/1Y0B6THLU6ZZPcXx_Jc62eZ2h9-9qw96h/view?usp=drive_link"
  "https://drive.google.com/file/d/18WPZg86aw7fKdA7LU-lCztiDrggAeF4s/view?usp=drive_link"
  "https://drive.google.com/file/d/19R3BOE_XpthkH3ia8CXE2SVsJZHjfMA_/view?usp=drive_link"
  "https://drive.google.com/file/d/1WeH5_1ysaqmDvgwoX1yUmTSLj_BkTZg-/view?usp=drive_link"
  "https://drive.google.com/file/d/1T4rGc6S3cb5m4PrmJKkvJZnVd92wLYWh/view?usp=drive_link"
)

echo "Downloading VQDM dataset..."
for url in "${links[@]}"; do
  echo "Downloading from $url..."
  gdown --fuzzy "$url"
done

echo "All downloads complete!"
