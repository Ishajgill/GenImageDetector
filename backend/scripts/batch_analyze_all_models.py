"""
Batch analysis script to test all models via API endpoint.
Outputs per-file results and comprehensive performance analysis.
"""
import os
from pathlib import Path
from PIL import Image
import statistics
import sys
import requests
import base64
from io import BytesIO
from datetime import datetime
import argparse
import random


def image_to_base64(image_path):
    """Convert image to base64 string."""
    with Image.open(image_path) as img:
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"


def get_relative_path(image_path, data_base):
    """Get path relative to data folder."""
    try:
        return str(image_path.relative_to(data_base))
    except ValueError:
        # If not relative to data_base, use parent folder + filename
        return f"{image_path.parent.name}/{image_path.name}"


def analyze_directory_via_api(directory, label, data_base, api_url="http://localhost:8000/analyze", log_file=None, sample_size=None):
    """
    Analyze all images in a directory via API endpoint.
    
    Args:
        directory: Path to directory containing images
        label: "real" or "fake" for ground truth
        data_base: Base path for relative path calculation
        api_url: URL of the analyze endpoint
        log_file: File object to write logs to
        sample_size: If provided, randomly sample this many images
    
    Returns:
        Tuple of (results dict, file_results list)
        - results: Dictionary with model names as keys and list of confidence scores as values
        - file_results: List of tuples (relative_path, label, model_scores_dict)
    """
    directory = Path(directory)
    
    # Get all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
    image_files = sorted([f for f in directory.iterdir() 
                          if f.suffix.lower() in image_extensions])
    
    # Sample if requested
    if sample_size and sample_size < len(image_files):
        image_files = random.sample(image_files, sample_size)
        image_files.sort()
    
    total = len(image_files)
    msg = f"\nAnalyzing {total} {label} images from {directory.name}..."
    print(msg)
    
    # Store results per model and per file
    results = {}
    file_results = []
    
    for i, image_path in enumerate(image_files, 1):
        try:
            # Convert image to base64
            img_base64 = image_to_base64(image_path)
            
            # Make API request
            response = requests.post(api_url, json={"image": img_base64})
            response.raise_for_status()
            
            data = response.json()
            
            # Get relative path
            rel_path = get_relative_path(image_path, data_base)
            
            # Store confidences for each model
            for model_name, confidence in data.items():
                if model_name not in results:
                    results[model_name] = []
                results[model_name].append(confidence)
            
            # Store per-file result
            file_results.append((rel_path, label, data))
            
            # Log this file's results
            if log_file:
                model_scores = ",".join([f"{k}:{v:.1f}" for k, v in sorted(data.items())])
                log_file.write(f"{rel_path},{label},{model_scores}\n")
            
            # Update progress bar
            progress = i / total
            bar_length = 50
            filled = int(bar_length * progress)
            bar = '█' * filled + '░' * (bar_length - filled)
            progress_str = f'\r[{bar}] {i}/{total} ({progress*100:.1f}%)'
            sys.stdout.write(progress_str)
            sys.stdout.flush()
                
        except Exception as e:
            error_msg = f"\n  Error processing {image_path.name}: {e}"
            print(error_msg)
            if log_file:
                log_file.write(f"ERROR,{image_path.name},{str(e)}\n")
            continue
    
    print()  # New line after progress bar
    
    return results, file_results


def analyze_handpicked_directory_via_api(directory, data_base, api_url="http://localhost:8000/analyze", log_file=None, sample_size=None):
    """
    Analyze hand-picked images where filename indicates ground truth.
    Files starting with 'real-' are real, others are AI-generated.
    
    Args:
        directory: Path to directory containing images
        data_base: Base path for relative path calculation
        api_url: URL of the analyze endpoint
        log_file: File object to write logs to
        sample_size: If provided, randomly sample this many images
    
    Returns:
        Tuple of (real_results, fake_results, file_results)
        - real_results/fake_results: Dict with model names as keys and list of scores as values
        - file_results: List of tuples (relative_path, label, model_scores_dict)
    """
    directory = Path(directory)
    
    # Get all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
    image_files = sorted([f for f in directory.iterdir() 
                          if f.suffix.lower() in image_extensions])
    
    # Sample if requested
    if sample_size and sample_size < len(image_files):
        image_files = random.sample(image_files, sample_size)
        image_files.sort()
    
    total = len(image_files)
    msg = f"\nAnalyzing {total} hand-picked images from {directory.name}..."
    print(msg)
    
    # Store results per model, separated by real/fake
    real_results = {}
    fake_results = {}
    file_results = []
    
    for i, image_path in enumerate(image_files, 1):
        try:
            # Determine if real or fake based on filename
            is_real = image_path.name.startswith('real-')
            label = "real" if is_real else "fake"
            
            # Convert image to base64
            img_base64 = image_to_base64(image_path)
            
            # Make API request
            response = requests.post(api_url, json={"image": img_base64})
            
            if response.status_code != 200:
                error_msg = f"\n  API returned status {response.status_code} for {image_path.name}: {response.text}"
                print(error_msg)
                if log_file:
                    log_file.write(f"ERROR,{image_path.name},HTTP {response.status_code}\n")
                    log_file.flush()
                sys.exit(1)
            
            data = response.json()
            
            # Get relative path
            rel_path = get_relative_path(image_path, data_base)
            
            # Store confidences for each model
            target_results = real_results if is_real else fake_results
            for model_name, confidence in data.items():
                if model_name not in target_results:
                    target_results[model_name] = []
                target_results[model_name].append(confidence)
            
            # Store per-file result
            file_results.append((rel_path, label, data))
            
            # Log this file's results
            if log_file:
                model_scores = ",".join([f"{k}:{v:.1f}" for k, v in sorted(data.items())])
                log_file.write(f"{rel_path},{label},{model_scores}\n")
            
            # Log this file's results
            if log_file:
                model_scores = ",".join([f"{k}:{v:.1f}" for k, v in sorted(data.items())])
                log_file.write(f"{rel_path},{label},{model_scores}\n")
            
            # Update progress bar
            progress = i / total
            bar_length = 50
            filled = int(bar_length * progress)
            bar = '█' * filled + '░' * (bar_length - filled)
            progress_str = f'\r[{bar}] {i}/{total} ({progress*100:.1f}%)'
            sys.stdout.write(progress_str)
            sys.stdout.flush()
                
        except Exception as e:
            error_msg = f"\n  Error processing {image_path.name}: {e}"
            print(error_msg)
            if log_file:
                log_file.write(f"ERROR,{image_path.name},{str(e)}\n")
            continue
    
    print()  # New line after progress bar
    
    return real_results, fake_results, file_results


def print_performance_analysis(all_results, log_file=None):
    """
    Print comprehensive performance analysis for all models.
    
    Args:
        all_results: Dict with structure {dataset_name: {model_name: {"real": scores, "fake": scores}}}
        log_file: File object to write logs to
    """
    separator = "\n" + "="*80
    print(separator)
    if log_file:
        log_file.write(separator + "\n")
    
    header = "PERFORMANCE ANALYSIS BY MODEL"
    print(header)
    if log_file:
        log_file.write(header + "\n")
    
    print("="*80)
    if log_file:
        log_file.write("="*80 + "\n")
    
    # Get all unique model names
    all_models = set()
    for dataset_results in all_results.values():
        all_models.update(dataset_results.keys())
    
    # Analyze each model
    for model_name in sorted(all_models):
        print(f"\n{model_name}:")
        if log_file:
            log_file.write(f"\n{model_name}:\n")
        
        print("-" * 80)
        if log_file:
            log_file.write("-" * 80 + "\n")
        
        # Analyze performance on each dataset
        for dataset_name, dataset_results in all_results.items():
            if model_name not in dataset_results:
                continue
            
            model_data = dataset_results[model_name]
            real_scores = model_data.get("real", [])
            fake_scores = model_data.get("fake", [])
            
            if not real_scores and not fake_scores:
                continue
            
            print(f"\n  {dataset_name}:")
            if log_file:
                log_file.write(f"\n  {dataset_name}:\n")
            
            # Real images stats
            if real_scores:
                real_correct = sum(1 for s in real_scores if s > 50)
                real_accuracy = (real_correct / len(real_scores)) * 100
                real_mean = statistics.mean(real_scores)
                real_median = statistics.median(real_scores)
                
                lines = [
                    f"    Real Images: {len(real_scores)} images",
                    f"      Accuracy: {real_accuracy:.2f}% ({real_correct}/{len(real_scores)})",
                    f"      Mean confidence: {real_mean:.2f}%",
                    f"      Median confidence: {real_median:.2f}%",
                    f"      Range: {min(real_scores):.1f}% - {max(real_scores):.1f}%"
                ]
                for line in lines:
                    print(line)
                    if log_file:
                        log_file.write(line + "\n")
            
            # Fake images stats
            if fake_scores:
                fake_correct = sum(1 for s in fake_scores if s < 50)
                fake_accuracy = (fake_correct / len(fake_scores)) * 100
                fake_mean = statistics.mean(fake_scores)
                fake_median = statistics.median(fake_scores)
                
                lines = [
                    f"    Fake Images: {len(fake_scores)} images",
                    f"      Accuracy: {fake_accuracy:.2f}% ({fake_correct}/{len(fake_scores)})",
                    f"      Mean confidence: {fake_mean:.2f}%",
                    f"      Median confidence: {fake_median:.2f}%",
                    f"      Range: {min(fake_scores):.1f}% - {max(fake_scores):.1f}%"
                ]
                for line in lines:
                    print(line)
                    if log_file:
                        log_file.write(line + "\n")
            
            # Overall accuracy for this dataset
            if real_scores and fake_scores:
                total_correct = real_correct + fake_correct
                total_images = len(real_scores) + len(fake_scores)
                overall_accuracy = (total_correct / total_images) * 100
                
                line = f"    Overall: {overall_accuracy:.2f}% ({total_correct}/{total_images})"
                print(line)
                if log_file:
                    log_file.write(line + "\n")
    
    print("\n" + "="*80)
    if log_file:
        log_file.write("\n" + "="*80 + "\n")


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Batch analyze images through all models via API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python batch_analyze_all_models.py              # Analyze all images
  python batch_analyze_all_models.py --sample 50  # Analyze 50 random images from each dataset
  python batch_analyze_all_models.py -s 100       # Analyze 100 random images from each dataset
        """
    )
    parser.add_argument(
        '--sample', '-s',
        type=int,
        metavar='N',
        help='Randomly sample N images from each dataset (useful for quick testing)'
    )
    args = parser.parse_args()
    
    # Create logs directory
    log_dir = Path("logs/batch_analyze_all_models")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create timestamped log file
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    log_path = log_dir / f"{timestamp}.log"
    
    with open(log_path, 'w', encoding='utf-8') as log_file:
        header = f"Batch Analysis - All Models via API\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        if args.sample:
            header += f"Sample size: {args.sample} images per dataset\n"
        header += "\n"
        print(header)
        log_file.write(header)
        
        # Write CSV header
        log_file.write("=== PER-FILE RESULTS ===\n")
        log_file.write("file_path,ground_truth,model_scores\n")
        
        # API endpoint
        api_url = "http://localhost:8000/analyze"
        
        # Paths to validation images
        data_base = Path(r"C:\Users\allen\src\school\CIS-4961\data")
        real_dir = data_base / "midjourney" / "nature"
        fake_dir = data_base / "midjourney" / "ai"
        handpicked_dir = data_base / "hand-picked"
        
        # Store all results for final analysis
        all_results = {}
        
        # Analyze validation datasets
        validation_results = {}
        
        if real_dir.exists():
            real_results, _ = analyze_directory_via_api(real_dir, "real", data_base, api_url, log_file, args.sample)
            for model_name, scores in real_results.items():
                if model_name not in validation_results:
                    validation_results[model_name] = {}
                validation_results[model_name]["real"] = scores
        
        if fake_dir.exists():
            fake_results, _ = analyze_directory_via_api(fake_dir, "fake", data_base, api_url, log_file, args.sample)
            for model_name, scores in fake_results.items():
                if model_name not in validation_results:
                    validation_results[model_name] = {}
                validation_results[model_name]["fake"] = scores
        
        if validation_results:
            all_results["Validation Dataset (ImageNet vs Midjourney)"] = validation_results
        
        # Analyze hand-picked images (always analyze all - it's a small dataset)
        handpicked_results = {}
        
        if handpicked_dir.exists():
            hp_real_results, hp_fake_results, _ = analyze_handpicked_directory_via_api(
                handpicked_dir, data_base, api_url, log_file, sample_size=None
            )
            
            for model_name, scores in hp_real_results.items():
                if model_name not in handpicked_results:
                    handpicked_results[model_name] = {}
                handpicked_results[model_name]["real"] = scores
            
            for model_name, scores in hp_fake_results.items():
                if model_name not in handpicked_results:
                    handpicked_results[model_name] = {}
                handpicked_results[model_name]["fake"] = scores
        
        if handpicked_results:
            all_results["Hand-Picked Images (Diverse)"] = handpicked_results
        
        # Print comprehensive performance analysis
        log_file.write("\n")
        print_performance_analysis(all_results, log_file)
        
        footer = f"\nResults saved to: {log_path}"
        print(footer)
        log_file.write(footer + "\n")


if __name__ == "__main__":
    main()
