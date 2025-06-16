import os
import argparse
from PIL import Image, UnidentifiedImageError
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from datetime import datetime


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

DEFAULT_BASE_DIR_NAME = "random_images"
DEFAULT_BASE_DIR = os.path.join(SCRIPT_DIR, DEFAULT_BASE_DIR_NAME)

DEFAULT_OUTPUT_FILE_NAME = "scan_results.log"
DEFAULT_OUTPUT_FILE = os.path.join(SCRIPT_DIR, DEFAULT_OUTPUT_FILE_NAME)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"}


def is_image_file(filename):
    return any(filename.lower().endswith(ext) for ext in IMAGE_EXTENSIONS)


def is_good_image(path):
    try:
        if os.path.getsize(path) == 0:
            return "empty"
        with Image.open(path) as img:
            img.verify()
        return "good"
    except (UnidentifiedImageError, IOError, OSError):
        return "corrupt"


def scan_directory(base_path):
    image_paths = [
        os.path.join(root, file)
        for root, _, files in os.walk(base_path)
        for file in files
        if is_image_file(file)
    ]

    results = {"total": 0, "good": 0, "corrupt": 0, "empty": 0}

    with ThreadPoolExecutor() as executor:
        future_to_path = {
            executor.submit(is_good_image, path): path for path in image_paths
        }

        for future in tqdm(
            as_completed(future_to_path),
            total=len(image_paths),
            desc="Scanning images",
        ):
            try:
                result = future.result()
                results["total"] += 1
                results[result] += 1
            except Exception:
                results["corrupt"] += 1
                results["total"] += 1

    return results


def write_summary_to_file(base_path, stats, output_path):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"Scan Timestamp: {timestamp}",
        f"Scanned Directory: {base_path}",
        f"Total image files: {stats['total']}",
        f"Good images:       {stats['good']}",
        f"Corrupt images:    {stats['corrupt']}",
        f"Empty files:       {stats['empty']}",
        "-" * 40,
        "",
    ]
    with open(output_path, "a") as f:
        f.write("\n".join(lines))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Scan images and classify as good, corrupt, or empty."
    )
    parser.add_argument(
        "--base-dir",
        type=str,
        default=DEFAULT_BASE_DIR,
        help=f"Path to the directory to scan. Defaults to `./${DEFAULT_BASE_DIR_NAME}`.",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default=DEFAULT_OUTPUT_FILE,
        help=f"Path to the file where results are saved. Defaults to `./${DEFAULT_OUTPUT_FILE_NAME}`.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    BASE_DIR = args.base_dir
    OUTPUT_FILE = args.output_file
    stats = scan_directory(BASE_DIR)

    print("\nScan Summary:")
    print(f"Scanned Directory: {BASE_DIR}")
    print(f"Total image files: {stats['total']}")
    print(f"Good images:       {stats['good']}")
    print(f"Corrupt images:    {stats['corrupt']}")
    print(f"Empty files:       {stats['empty']}")

    write_summary_to_file(BASE_DIR, stats, OUTPUT_FILE)
    print(f"\nResults saved to {OUTPUT_FILE}")
