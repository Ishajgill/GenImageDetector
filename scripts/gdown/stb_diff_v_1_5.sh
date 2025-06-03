#!/bin/bash

BASE_DIR="/nfs/turbo/umd-anglial/GenImageDetector/raw_dataset_zip"
mkdir -p "$BASE_DIR"
cd "$BASE_DIR" || exit

STB_DIFF_V_1_5_DIR="$BASE_DIR/stable_diffusion_v_1_4"
mkdir -p "$STB_DIFF_V_1_5_DIR"
cd "$STB_DIFF_V_1_5_DIR" || exit

links=(
  "https://drive.google.com/file/d/1ndGh-3D8kaVFktogs_jhPkvXac90vzTh/view?usp=drive_link"
  "https://drive.google.com/file/d/1PAMShns8pmgdDvfMWcOSUwLlycsIIjBx/view?usp=drive_link"
  "https://drive.google.com/file/d/1L0GCM6Z5w59AAxCZ4HEhwqupzL2FbkOx/view?usp=drive_link"
  "https://drive.google.com/file/d/1RKfdsJE_psjqccPfqzcnHYX9QCjpSdRP/view?usp=drive_link"
  "https://drive.google.com/file/d/1C7GgeEY8a3fYnAepQiKrZlPK6beo7C4L/view?usp=drive_link"
  "https://drive.google.com/file/d/1VKU3G-iogKHOC_WKNF50q0JHHRxFnPgs/view?usp=drive_link"
  "https://drive.google.com/file/d/1RBsppKpJvG1nFtDTvX5XRTTC-m9_nAEC/view?usp=drive_link"
  "https://drive.google.com/file/d/1wuxr0vwip9oNJPQpvjcM7xf8Ucc8EPIn/view?usp=drive_link"
  "https://drive.google.com/file/d/1dQ4acDwkDCV7c77sKdjhllVcNxb1v0kr/view?usp=drive_link"
  "https://drive.google.com/file/d/1Go2IKo-Ov5G90YSugSWyGk9B0xbotLEC/view?usp=drive_link"
  "https://drive.google.com/file/d/1imOdemMa3_uIwLVXcrZhZtAnfOvK9dos/view?usp=drive_link"
  "https://drive.google.com/file/d/1cw5CIdyEBaPOMzRZJ1M7or-Svcf_4H6B/view?usp=drive_link"
  "https://drive.google.com/file/d/14ycTQh2hsPFYD3wbFCF-MFZVfpju7JNo/view?usp=drive_link"
  "https://drive.google.com/file/d/13k4XPf790f58VcxHslr-8-7Fc52Qnfez/view?usp=drive_link"
  "https://drive.google.com/file/d/1NVh7_-_98JxEBb1YQ09_MjtkjZK_QtUg/view?usp=drive_link"
  "https://drive.google.com/file/d/1N6Z7p-zw357pJ_ttdeq7d0kP583DneTP/view?usp=drive_link"
  "https://drive.google.com/file/d/1N4KqSFq52xY8vMHO-ORsJwQ1V_1gM5sE/view?usp=drive_link"
  "https://drive.google.com/file/d/1TO78Dzetf5tWca-5gqVFdS5i6-FvH3du/view?usp=drive_link"
  "https://drive.google.com/file/d/1XfX0XbEMANeI5nOtHP-uDncxjZQUHTDy/view?usp=drive_link"
  "https://drive.google.com/file/d/1RIcrlEWGVKYfvnL9ic8WuOu40e29IZxD/view?usp=drive_link"
  "https://drive.google.com/file/d/10JkLaB6c6hI5MYPLO8W8QiNuTTZDs0K5/view?usp=drive_link"
  "https://drive.google.com/file/d/10I0YpTZUH_jpOkueqPLma7VvyDW6xtMc/view?usp=drive_link"
  "https://drive.google.com/file/d/10GpQt93_vVI-9lQFpBqRW2Yj7OBW19_y/view?usp=drive_link"
  "https://drive.google.com/file/d/1097eSe5HjuU0TjQ3R_qH6JPnz1pQmnps/view?usp=drive_link"
  "https://drive.google.com/file/d/106k_cX01UsnjfH3Y867xh5y3sGTysdyM/view?usp=drive_link"
  "https://drive.google.com/file/d/1thjlQZsGUwVxr8ZvZATZT2x33x4CeeMX/view?usp=drive_link"
  "https://drive.google.com/file/d/1i4cwgOgZSDM9yutyEjZxgn9Uwrr14Z13/view?usp=drive_link"
  "https://drive.google.com/file/d/1tZHiDccnGJRNvFPelah9o-zsAS4sWi9E/view?usp=drive_link"
  "https://drive.google.com/file/d/1UclAz1ydKegS5_5S4xSvlP78qR_7Pvu4/view?usp=drive_link"
  "https://drive.google.com/file/d/1ij9QGjkvknlSV8MQEvhs1I9d60i6WvEZ/view?usp=drive_link"
  "https://drive.google.com/file/d/16fpAiTn9cKJxhdAZYUMQWq8IiiIHEy_T/view?usp=drive_link"
)

echo "Downloading Stable Diffusion v1.5 dataset..."
for url in "${links[@]}"; do
  echo "Downloading from $url..."
  gdown --fuzzy "$url"
done

echo "All downloads complete!"
