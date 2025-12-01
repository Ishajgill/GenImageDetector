"""
Batch analysis script to test CNNSpot classifier on validation images.
"""
import os
from pathlib import Path
from PIL import Image
import statistics
import sys
from datetime import datetime
from io import StringIO

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from classifiers.cnnspot import CNNSpotClassifier


def analyze_directory(classifier, directory, label):
    """
    Analyze all images in a directory.

    Args:
        classifier: CNNSpotClassifier instance
        directory: Path to directory containing images
        label: "real" or "fake" for ground truth

    Returns:
        List of confidence scores
    """
    scores = []
    directory = Path(directory)

    # Get all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.JPEG'}
    image_files = [f for f in directory.iterdir()
                   if f.suffix in image_extensions]

    total = len(image_files)
    print(f"\nAnalyzing {total} {label} images from {directory.name}...")

    for i, image_path in enumerate(image_files, 1):
        try:
            # Open and analyze image
            img = Image.open(image_path).convert('RGB')
            confidence = classifier.analyze(img)
            scores.append(confidence)

            # Update progress bar (simple ASCII version for Windows)
            progress = i / total
            bar_length = 50
            filled = int(bar_length * progress)
            bar = '=' * filled + '-' * (bar_length - filled)
            sys.stdout.write(f'\r[{bar}] {i}/{total} ({progress*100:.1f}%)')
            sys.stdout.flush()

        except Exception as e:
            print(f"\n  Error processing {image_path.name}: {e}")
            continue

    print()  # New line after progress bar
    return scores


def analyze_handpicked_directory(classifier, directory):
    """
    Analyze hand-picked images where filename indicates ground truth.
    Files starting with 'real-' are real, others are AI-generated.

    Args:
        classifier: CNNSpotClassifier instance
        directory: Path to directory containing images

    Returns:
        Tuple of (real_scores, fake_scores)
    """
    real_scores = []
    fake_scores = []
    directory = Path(directory)

    # Get all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
    image_files = [f for f in directory.iterdir()
                   if f.suffix.lower() in image_extensions]

    total = len(image_files)
    print(f"\nAnalyzing {total} hand-picked images from {directory.name}...")

    for i, image_path in enumerate(image_files, 1):
        try:
            # Determine if real or fake based on filename
            is_real = image_path.name.startswith('real-')

            # Open and analyze image
            img = Image.open(image_path).convert('RGB')
            confidence = classifier.analyze(img)

            if is_real:
                real_scores.append(confidence)
            else:
                fake_scores.append(confidence)

            # Update progress bar (simple ASCII version for Windows)
            progress = i / total
            bar_length = 50
            filled = int(bar_length * progress)
            bar = '=' * filled + '-' * (bar_length - filled)
            sys.stdout.write(f'\r[{bar}] {i}/{total} ({progress*100:.1f}%)')
            sys.stdout.flush()

        except Exception as e:
            print(f"\n  Error processing {image_path.name}: {e}")
            continue

    print()  # New line after progress bar
    return real_scores, fake_scores


def print_statistics_logged(scores, label, log_buffer):
    """Print statistics for a set of scores and log them."""
    if not scores:
        msg = f"\n{label.upper()} Images: No valid scores"
        print(msg)
        log_buffer.write(msg + "\n")
        return

    def print_and_log(msg):
        print(msg)
        log_buffer.write(msg + "\n")

    print_and_log(f"\n{label.upper()} Images Statistics:")
    print_and_log(f"  Number of images: {len(scores)}")
    print_and_log(f"  Mean confidence: {statistics.mean(scores):.2f}%")
    print_and_log(f"  Median confidence: {statistics.median(scores):.2f}%")
    print_and_log(f"  Min confidence: {min(scores):.2f}%")
    print_and_log(f"  Max confidence: {max(scores):.2f}%")
    print_and_log(f"  Std deviation: {statistics.stdev(scores) if len(scores) > 1 else 0:.2f}%")

    # Accuracy (for real: >50%, for fake: <50%)
    if label == "real" or "real" in label.lower():
        correct = sum(1 for s in scores if s > 50)
    else:  # fake
        correct = sum(1 for s in scores if s < 50)

    accuracy = (correct / len(scores)) * 100
    print_and_log(f"  Accuracy: {accuracy:.2f}% ({correct}/{len(scores)})")


def main():
    # Capture output for logging
    log_buffer = StringIO()

    # Initialize classifier in quiet mode
    model_path = "models/CNNSpot/2025_10_22_epoch_best.pth"
    msg = f"Loading CNNSpot model from {model_path}..."
    print(msg)
    log_buffer.write(msg + "\n")

    classifier = CNNSpotClassifier(model_path, quiet=True)

    # Paths to validation images
    real_dir = Path(r"C:\Users\allen\src\school\CIS-4961\GenImageDetector\data\midjourney\nature")
    fake_dir = Path(r"C:\Users\allen\src\school\CIS-4961\GenImageDetector\data\midjourney\ai")
    handpicked_dir = Path(r"C:\Users\allen\src\school\CIS-4961\GenImageDetector\data\hand-picked")

    # Analyze validation datasets
    real_scores = []
    fake_scores = []

    if real_dir.exists():
        real_scores = analyze_directory(classifier, real_dir, "real")

    if fake_dir.exists():
        fake_scores = analyze_directory(classifier, fake_dir, "fake")

    # Analyze hand-picked images
    handpicked_real_scores = []
    handpicked_fake_scores = []

    if handpicked_dir.exists():
        handpicked_real_scores, handpicked_fake_scores = analyze_handpicked_directory(classifier, handpicked_dir)

    # Print and capture results
    def print_and_log(msg):
        print(msg)
        log_buffer.write(msg + "\n")

    print_and_log("\n" + "="*60)
    print_and_log("BATCH ANALYSIS RESULTS")
    print_and_log("="*60)

    if real_scores:
        print_and_log("\n--- VALIDATION DATASET ---")
        print_statistics_logged(real_scores, "real", log_buffer)
        print_statistics_logged(fake_scores, "fake", log_buffer)

    if handpicked_real_scores or handpicked_fake_scores:
        print_and_log("\n--- HAND-PICKED IMAGES ---")
        if handpicked_real_scores:
            print_statistics_logged(handpicked_real_scores, "real (hand-picked)", log_buffer)
        if handpicked_fake_scores:
            print_statistics_logged(handpicked_fake_scores, "fake (hand-picked)", log_buffer)

    # Overall accuracy for validation dataset
    if real_scores and fake_scores:
        total_correct = (
            sum(1 for s in real_scores if s > 50) +
            sum(1 for s in fake_scores if s < 50)
        )
        total_images = len(real_scores) + len(fake_scores)
        overall_accuracy = (total_correct / total_images) * 100

        print_and_log(f"\n{'='*60}")
        print_and_log(f"VALIDATION OVERALL ACCURACY: {overall_accuracy:.2f}% ({total_correct}/{total_images})")
        print_and_log(f"{'='*60}")

    # Overall accuracy for hand-picked images
    if handpicked_real_scores or handpicked_fake_scores:
        total_correct = (
            sum(1 for s in handpicked_real_scores if s > 50) +
            sum(1 for s in handpicked_fake_scores if s < 50)
        )
        total_images = len(handpicked_real_scores) + len(handpicked_fake_scores)
        overall_accuracy = (total_correct / total_images) * 100

        print_and_log(f"\n{'='*60}")
        print_and_log(f"HAND-PICKED OVERALL ACCURACY: {overall_accuracy:.2f}% ({total_correct}/{total_images})")
        print_and_log(f"{'='*60}\n")

    # Save log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = Path("logs/batch_analyze")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{timestamp}.log"

    with open(log_file, 'w') as f:
        f.write(log_buffer.getvalue())

    print(f"\nLog saved to: {log_file}")


def print_statistics_logged(scores, label, log_buffer):
    """Print statistics for a set of scores and log them."""
    if not scores:
        msg = f"\n{label.upper()} Images: No valid scores"
        print(msg)
        log_buffer.write(msg + "\n")
        return

    def print_and_log(msg):
        print(msg)
        log_buffer.write(msg + "\n")

    print_and_log(f"\n{label.upper()} Images Statistics:")
    print_and_log(f"  Number of images: {len(scores)}")
    print_and_log(f"  Mean confidence: {statistics.mean(scores):.2f}%")
    print_and_log(f"  Median confidence: {statistics.median(scores):.2f}%")
    print_and_log(f"  Min confidence: {min(scores):.2f}%")
    print_and_log(f"  Max confidence: {max(scores):.2f}%")
    print_and_log(f"  Std deviation: {statistics.stdev(scores) if len(scores) > 1 else 0:.2f}%")

    # Accuracy (for real: >50%, for fake: <50%)
    if label == "real" or "real" in label.lower():
        correct = sum(1 for s in scores if s > 50)
    else:  # fake
        correct = sum(1 for s in scores if s < 50)

    accuracy = (correct / len(scores)) * 100
    print_and_log(f"  Accuracy: {accuracy:.2f}% ({correct}/{len(scores)})")


def main():
    # Capture output for logging
    log_buffer = StringIO()

    # Initialize classifier in quiet mode
    model_path = "models/CNNSpot/2025_10_22_epoch_best.pth"
    msg = f"Loading CNNSpot model from {model_path}..."
    print(msg)
    log_buffer.write(msg + "\n")

    classifier = CNNSpotClassifier(model_path, quiet=True)

    # Paths to validation images
    real_dir = Path(r"C:\Users\allen\src\school\CIS-4961\GenImageDetector\data\midjourney\nature")
    fake_dir = Path(r"C:\Users\allen\src\school\CIS-4961\GenImageDetector\data\midjourney\ai")
    handpicked_dir = Path(r"C:\Users\allen\src\school\CIS-4961\GenImageDetector\data\hand-picked")

    # Analyze validation datasets
    real_scores = []
    fake_scores = []

    if real_dir.exists():
        real_scores = analyze_directory(classifier, real_dir, "real")

    if fake_dir.exists():
        fake_scores = analyze_directory(classifier, fake_dir, "fake")

    # Analyze hand-picked images
    handpicked_real_scores = []
    handpicked_fake_scores = []

    if handpicked_dir.exists():
        handpicked_real_scores, handpicked_fake_scores = analyze_handpicked_directory(classifier, handpicked_dir)

    # Print and capture results
    def print_and_log(msg):
        print(msg)
        log_buffer.write(msg + "\n")

    print_and_log("\n" + "="*60)
    print_and_log("BATCH ANALYSIS RESULTS")
    print_and_log("="*60)

    if real_scores:
        print_and_log("\n--- VALIDATION DATASET ---")
        print_statistics_logged(real_scores, "real", log_buffer)
        print_statistics_logged(fake_scores, "fake", log_buffer)

    if handpicked_real_scores or handpicked_fake_scores:
        print_and_log("\n--- HAND-PICKED IMAGES ---")
        if handpicked_real_scores:
            print_statistics_logged(handpicked_real_scores, "real (hand-picked)", log_buffer)
        if handpicked_fake_scores:
            print_statistics_logged(handpicked_fake_scores, "fake (hand-picked)", log_buffer)

    # Overall accuracy for validation dataset
    if real_scores and fake_scores:
        total_correct = (
            sum(1 for s in real_scores if s > 50) +
            sum(1 for s in fake_scores if s < 50)
        )
        total_images = len(real_scores) + len(fake_scores)
        overall_accuracy = (total_correct / total_images) * 100

        print_and_log(f"\n{'='*60}")
        print_and_log(f"VALIDATION OVERALL ACCURACY: {overall_accuracy:.2f}% ({total_correct}/{total_images})")
        print_and_log(f"{'='*60}")

    # Overall accuracy for hand-picked images
    if handpicked_real_scores or handpicked_fake_scores:
        total_correct = (
            sum(1 for s in handpicked_real_scores if s > 50) +
            sum(1 for s in handpicked_fake_scores if s < 50)
        )
        total_images = len(handpicked_real_scores) + len(handpicked_fake_scores)
        overall_accuracy = (total_correct / total_images) * 100

        print_and_log(f"\n{'='*60}")
        print_and_log(f"HAND-PICKED OVERALL ACCURACY: {overall_accuracy:.2f}% ({total_correct}/{total_images})")
        print_and_log(f"{'='*60}\n")

    # Save log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = Path("logs/batch_analyze")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{timestamp}.log"

    with open(log_file, 'w') as f:
        f.write(log_buffer.getvalue())

    print(f"\nLog saved to: {log_file}")


if __name__ == "__main__":
    main()
