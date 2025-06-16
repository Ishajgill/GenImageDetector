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


def is_good_image(path, delete_bad=False, deleted_log=None):
    try:
        if os.path.getsize(path) == 0:
            if delete_bad:
                os.remove(path)
                if deleted_log is not None:
                    deleted_log.append((path, "empty"))
            return "empty"
        with Image.open(path) as img:
            img.verify()
        return "good"
    except (UnidentifiedImageError, IOError, OSError):
        if delete_bad:
            try:
                os.remove(path)
                if deleted_log is not None:
                    deleted_log.append((path, "corrupt"))
            except Exception as e:
                if deleted_log is not None:
                    deleted_log.append((path, f"delete_failed: {e}"))
        return "corrupt"


def scan_directory(base_path, delete_bad=False):
    per_folder_results = {}
    image_tasks = []
    deleted_files = []

    for root, _, files in os.walk(base_path):
        folder_key = os.path.relpath(root, base_path)
        per_folder_results[folder_key] = {
            "total": 0,
            "good": 0,
            "corrupt": 0,
            "empty": 0,
        }

        for file in files:
            if is_image_file(file):
                full_path = os.path.join(root, file)
                image_tasks.append((full_path, folder_key))
                per_folder_results[folder_key]["total"] += 1

    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(
                is_good_image, path, delete_bad, deleted_files
            ): folder_key
            for path, folder_key in image_tasks
        }

        for future in tqdm(
            as_completed(futures), total=len(futures), desc="Scanning images"
        ):
            try:
                result = future.result()
                folder = futures[future]
                per_folder_results[folder][result] += 1
            except Exception:
                folder = futures[future]
                per_folder_results[folder]["corrupt"] += 1
                per_folder_results[folder]["total"] += 1

    return per_folder_results, deleted_files


def write_summary_to_file(
    per_folder_results, deleted_files, output_path, scanned_path
):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"Scan Timestamp: {timestamp}",
        f"Scanned Directory: {scanned_path}",
        "",
        "Per-folder Results:",
    ]

    total_summary = {"total": 0, "good": 0, "corrupt": 0, "empty": 0}

    for folder, stats in sorted(per_folder_results.items()):
        lines.append(f"[{folder}]")
        for k in ["total", "good", "corrupt", "empty"]:
            lines.append(f"  {k.capitalize():<8}: {stats[k]}")
            total_summary[k] += stats[k]
        lines.append("")

    lines.append("-" * 40)
    lines.append("Total Summary:")
    for k in ["total", "good", "corrupt", "empty"]:
        lines.append(f"{k.capitalize():<8}: {total_summary[k]}")
    lines.append("")

    if deleted_files:
        lines.append("Deleted Files:")
        for path, reason in deleted_files:
            lines.append(f"{reason:<12} {path}")
        lines.append("")

    with open(output_path, "a") as f:
        f.write("\n".join(lines) + "\n")


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
    parser.add_argument(
        "--delete-bad",
        action="store_true",
        help="If set, deletes corrupt and empty image files as they are detected.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    per_folder_results, deleted_files = scan_directory(
        args.base_dir, delete_bad=args.delete_bad
    )

    print("\nPer-folder Summary:")
    for folder, stats in sorted(per_folder_results.items()):
        print(f"[{folder}]")
        for k in ["total", "good", "corrupt", "empty"]:
            print(f"  {k.capitalize():<8}: {stats[k]}")
        print()

    if args.delete_bad and deleted_files:
        print(f"{len(deleted_files)} files deleted.")

    write_summary_to_file(
        per_folder_results, deleted_files, args.output_file, args.base_dir
    )
    print(f"\nResults saved to {args.output_file}")
