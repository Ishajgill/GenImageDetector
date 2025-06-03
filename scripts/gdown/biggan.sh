#!/bin/bash

BASE_DIR="/nfs/turbo/umd-anglial/GenImageDetector/raw_dataset_zip"
mkdir -p "$BASE_DIR"
cd "$BASE_DIR" || exit

BIGGAN_DIR="$BASE_DIR/biggan"
mkdir -p "$BIGGAN_DIR"
cd "$BIGGAN_DIR" || exit

links=(
  "https://drive.google.com/file/d/1dtuXpn2MDGRVSrzZwZvKWtQA6yO3U6u5/view?usp=drive_link" # .z01
  "https://drive.google.com/file/d/1-ECWWWXDEwDlBz4CBALSThZfyg0eGBm9/view?usp=drive_link" # .z02
  "https://drive.google.com/file/d/16PPUE9XcHndSprOcTPHVuDsZPyApyfF_/view?usp=drive_link" # .z03
  "https://drive.google.com/file/d/1pOyRWuy5U7aHhELEuu_0dzbxdq4ZxWYR/view?usp=drive_link" # .z04
  "https://drive.google.com/file/d/1mJDGWC4yYqViT_4V2v56Ww8G39G7LoF0/view?usp=drive_link" # .z05
  "https://drive.google.com/file/d/1d32eMbi9T2McdSPDfMZWk25NNrIvmK90/view?usp=drive_link" # .z06
  "https://drive.google.com/file/d/1dAy2qpQmh7c7Ye6Awje-Wku7LaJUxFpS/view?usp=drive_link" # .z07
  "https://drive.google.com/file/d/1TRTjKdrJPEvLaP-O_31nrlnAsqRO6n8R/view?usp=drive_link" # .zip
)

echo "Downloading BigGAN dataset..."
for url in "${links[@]}"; do
  echo "Downloading from $url..."
  gdown --fuzzy "$url"
done

echo "All downloads complete!"
