#!/bin/bash

BASE_DIR="/nfs/turbo/umd-anglial/GenImageDetector/raw_dataset_zip"
mkdir -p "$BASE_DIR"
cd "$BASE_DIR" || exit

STB_DIFF_V_1_4_DIR="$BASE_DIR/stable_diffusion_v_1_4"
mkdir -p "$STB_DIFF_V_1_4_DIR"
cd "$STB_DIFF_V_1_4_DIR" || exit

links=(
  "https://drive.google.com/file/d/1Y7FZMVzopwXaPIeMwpBYNiI7IWxENgFU/view?usp=drive_link"
  "https://drive.google.com/file/d/1Z-vL01F3QkTilJvuYN_jqOTIQ8QvmAGy/view?usp=drive_link"
  "https://drive.google.com/file/d/1hS777nqeBbkfKWs-7axGNomIcnRDTCsE/view?usp=drive_link"
  "https://drive.google.com/file/d/17E-BPsGiVLfsAKwkyHG2pPxLuUBOjTZ4/view?usp=drive_link"
  "https://drive.google.com/file/d/1MWJb1adBFgsGdbm96PcvV0Idf_t-UUoF/view?usp=drive_link"
  "https://drive.google.com/file/d/1qmjicansM2-2hECrmBrrlgoC8azzl-lL/view?usp=drive_link"
  "https://drive.google.com/file/d/1GB6jvADz8SYKi6lq5RJGGpFnRuOmV1GP/view?usp=drive_link"
  "https://drive.google.com/file/d/15SM5PwbYyZHoALi2uhvSbQkBhbmNKvhX/view?usp=drive_link"
  "https://drive.google.com/file/d/15E4Scf99aXBP7n56uJ0NzkUO4acxGBT_/view?usp=drive_link"
  "https://drive.google.com/file/d/1HZLd0sSrzgNM0j3VR1EUdrzrzipd6WN6/view?usp=drive_link"
  "https://drive.google.com/file/d/1IMk7wMq-Fcb4pw9RhAQ3DgyWAqVWTzZa/view?usp=drive_link"
  "https://drive.google.com/file/d/10Ibi1VVVbMQG7WQX6ZTlpJRtsOyWfAI5/view?usp=drive_link"
  "https://drive.google.com/file/d/1qNSC7OT22c2n_8sOI1pfO_9A9-c4vnGN/view?usp=drive_link"
  "https://drive.google.com/file/d/1te2oARoJy-UQp-Mgf26eLda16S6Ir6ef/view?usp=drive_link"
  "https://drive.google.com/file/d/1PeNQJBYLGbmOprFlTjynrSZ0r1-34Poo/view?usp=drive_link"
  "https://drive.google.com/file/d/1T1z3dcEQ0q-WWhwq24ulAjVy3G_O8cZ7/view?usp=drive_link"
  "https://drive.google.com/file/d/1hSoaXOK-2mQK3lZ_QcSAGP8YPl12wgGS/view?usp=drive_link"
  "https://drive.google.com/file/d/1lHVRAS5453b2B3KErG0YXSF2Z3BoXkLn/view?usp=drive_link"
  "https://drive.google.com/file/d/1cju9hbC5IUMp8lsRsqS5lsL033PwabY9/view?usp=drive_link"
  "https://drive.google.com/file/d/1ysCGAz0XlPjjQGGjR2zWEVfrP0XIkiWp/view?usp=drive_link"
  "https://drive.google.com/file/d/1PianQ6okcy3VmYfKcnVriqpTmoxO2Z46/view?usp=drive_link"
  "https://drive.google.com/file/d/1NlQJhIl1Qpl8Cw2LwZGqVC0yQzSyJM-d/view?usp=drive_link"
  "https://drive.google.com/file/d/1DqvN2kkZA5j4PDRSRATuBUQsYluMnYbW/view?usp=drive_link"
  "https://drive.google.com/file/d/1RFYGzREYM8qfX-afUSOlYZKW81MhHKur/view?usp=drive_link"
  "https://drive.google.com/file/d/118SonC2aFvNnTbka335QzzTjQ-Nybwd-/view?usp=drive_link"
  "https://drive.google.com/file/d/1luJplS8nutHIs_3wDU6cDtySbntFHRgj/view?usp=drive_link"
  "https://drive.google.com/file/d/1AdD5yNX_Z5v70oqzAgp9gHxhZ0OKXgM0/view?usp=drive_link"
  "https://drive.google.com/file/d/1v6DK-8YNG7w5qUafk1JT1-B17vvThh37/view?usp=drive_link"
  "https://drive.google.com/file/d/1b6_70ptyHRd8wEiUc9lq_N4OLuyf_bTK/view?usp=drive_link"
  "https://drive.google.com/file/d/1gPjgbo5ZYyOW_PBhOeQB47CPLL6nqEjs/view?usp=drive_link"
)

echo "Downloading Stable Diffusion v1.4 dataset..."
for url in "${links[@]}"; do
  echo "Downloading from $url..."
  gdown --fuzzy "$url"
done

echo "All downloads complete!"
