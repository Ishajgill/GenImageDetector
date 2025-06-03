#!/bin/bash

BASE_DIR="/nfs/turbo/umd-anglial/GenImageDetector/raw_dataset_zip"
mkdir -p "$BASE_DIR"
cd "$BASE_DIR" || exit

GLIDE_DIR="$BASE_DIR/glide"
mkdir -p "$GLIDE_DIR"
cd "$GLIDE_DIR" || exit

links=(
  "https://drive.google.com/file/d/1NvEr9FSMhc28qxt2RsfSHyRoVm06YbO6/view?usp=drive_link" # .z01
  "https://drive.google.com/file/d/15BwJz-Iq5ealHgtiFau10n28WhRGvGGR/view?usp=drive_link" # .z02
  "https://drive.google.com/file/d/1O0uEfzUlYcojOVqTpjF7AI3P9mFU2ooE/view?usp=drive_link" # .z03
  "https://drive.google.com/file/d/1SzGYBOYsWX3SwwJt51oZIDIzt3JBzzVA/view?usp=drive_link" # .z04
  "https://drive.google.com/file/d/1Du_7BEFuXzKGqI-bSvi3FWXWlFmUf5K3/view?usp=drive_link" # .z05
  "https://drive.google.com/file/d/1TVTNRKtS3Tl1ovmej5u9Flg7yqHgCadQ/view?usp=drive_link" # .z06
  "https://drive.google.com/file/d/1LssUx4DjLOHrv8hD8MCY4u1ADfHrOXHc/view?usp=drive_link" # .z07
  "https://drive.google.com/file/d/1ws3dqHTCAwteaf950YWMGl_MYKr0kTp3/view?usp=drive_link" # .z08
  "https://drive.google.com/file/d/1iUtbABfaGZPGxgJDmFFqgsYqogUFFtma/view?usp=drive_link" # .z09
  "https://drive.google.com/file/d/1IAo3GYGFR3vbExTjCZxwQ9RPdYhoNncA/view?usp=drive_link" # .z10
  "https://drive.google.com/file/d/1npimXkkd74IkzkBChduvlkQWQTUhP8CA/view?usp=drive_link" # .zip
)

echo "Downloading GLIDE dataset..."
for url in "${links[@]}"; do
  echo "Downloading from $url..."
  gdown --fuzzy "$url"
done

echo "All downloads complete!"
