#!/bin/bash

BASE_DIR="/nfs/turbo/umd-anglial/GenImageDetector/raw_dataset_zip"
mkdir -p "$BASE_DIR"
cd "$BASE_DIR" || exit

ADM_DIR="$BASE_DIR/adm"
mkdir -p "$ADM_DIR"
cd "$ADM_DIR" || exit

links=(
  "https://drive.google.com/file/d/1UsKnM31nMmTj8kOULDcL001RgvkytivX/view?usp=drive_link" # .z01
  "https://drive.google.com/file/d/16LJLkjwMogqudCtocdwiRu-68ADTS0n_/view?usp=drive_link" # .z02
  "https://drive.google.com/file/d/1MN5tCrwkvbD1YutPlxAZN3eySg65PyEg/view?usp=drive_link" # .z03
  "https://drive.google.com/file/d/1_rnhlIWoEpLbhvwr94_6gAx-VbIQicS6/view?usp=drive_link" # .z04
  "https://drive.google.com/file/d/18Mx1Std1ZegdUYiFEp2PW8EhD2tYmSRz/view?usp=drive_link" # .z05
  "https://drive.google.com/file/d/1BI9ra0fRIm8BHp9EH9P9w9Kk3E3PQsbw/view?usp=drive_link" # .z06
  "https://drive.google.com/file/d/1xPccO2q3fe2qiQtwH0tm-eC9_HGgLkdN/view?usp=drive_link" # .z07
  "https://drive.google.com/file/d/1hE5wOXxxBnaeCScjAV1SMXl-8xYuP8Rr/view?usp=drive_link" # .z08
  "https://drive.google.com/file/d/1abhNcONyuWKSOyL3BGyW94YlVUvmvog6/view?usp=drive_link" # .z09
  "https://drive.google.com/file/d/1Ne9yPLskS-Mo07EJM4trcvwGEr78Esbq/view?usp=drive_link" # .z10
  "https://drive.google.com/file/d/1vivg0FuaGo1eYRhSHcxloKXGfob1Shc2/view?usp=drive_link" # .z11
  "https://drive.google.com/file/d/1Wr30-38zcq3QCmo4zFd4ohX3Xi9KgXqh/view?usp=drive_link" # .z12
  "https://drive.google.com/file/d/1kappILSn-kzBxja9GPw6JpGrzxFTl9rD/view?usp=drive_link" # .zip
)

echo "Downloading ADM dataset..."
for url in "${links[@]}"; do
  echo "Downloading from $url..."
  gdown --fuzzy "$url"
done

echo "All downloads complete!"
