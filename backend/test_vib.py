from pathlib import Path
from statistics import mean
from huggingface_hub import hf_hub_download
from PIL import Image

from ml.classifiers.vib import VIBClassifier


MODEL_PATH = hf_hub_download(
    repo_id="danielcobb/GenImageDetector-weights",
    filename="best.pth",
)

TEST_ROOT = Path(
    r"C:\Users\gillc\Downloads\vib_test"
)

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}


def collect_images(folder: Path) -> list[Path]:
    return sorted(
        path
        for path in folder.iterdir()
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def test_folder(
    classifier: VIBClassifier,
    folder: Path,
    expected_label: str,
) -> list[float]:
    scores = []

    image_paths = collect_images(folder)

    if not image_paths:
        print(f"No images found in: {folder}")
        return scores

    print()
    print(f"Testing folder: {folder}")
    print("-" * 90)

    for image_path in image_paths:
        try:
            with Image.open(image_path) as image:
                image = image.convert("RGB")
                real_confidence = classifier.analyze(image)

            prediction = (
                "REAL"
                if real_confidence >= 50
                else "AI"
            )

            correct = prediction == expected_label

            scores.append(real_confidence)

            print(
                f"{image_path.name:35} "
                f"{real_confidence:6.1f}% real   "
                f"Prediction: {prediction:4}   "
                f"{'CORRECT' if correct else 'WRONG'}"
            )

        except Exception as error:
            print(
                f"{image_path.name:35} "
                f"ERROR: {error}"
            )

    return scores


def main() -> None:
    real_folder = TEST_ROOT / "real"
    ai_folder = TEST_ROOT / "ai"

    if not real_folder.exists():
        raise FileNotFoundError(
            f"Missing real folder: {real_folder}"
        )

    if not ai_folder.exists():
        raise FileNotFoundError(
            f"Missing AI folder: {ai_folder}"
        )

    classifier = VIBClassifier(
        model_path=MODEL_PATH,
        device="cpu",
        quiet=False,
    )

    print()
    print("Model training mode:", classifier.model.training)
    print("Transform:")
    print(classifier.transform)

    real_scores = test_folder(
        classifier=classifier,
        folder=real_folder,
        expected_label="REAL",
    )

    ai_scores = test_folder(
        classifier=classifier,
        folder=ai_folder,
        expected_label="AI",
    )

    print()
    print("=" * 90)
    print("SUMMARY")
    print("=" * 90)

    if real_scores:
        print(
            "Average real confidence for real images:",
            round(mean(real_scores), 1),
        )

    if ai_scores:
        print(
            "Average real confidence for AI images:",
            round(mean(ai_scores), 1),
        )

    if real_scores and ai_scores:
        real_correct = sum(
            score >= 50
            for score in real_scores
        )

        ai_correct = sum(
            score < 50
            for score in ai_scores
        )

        total_correct = real_correct + ai_correct
        total_images = len(real_scores) + len(ai_scores)

        print(
            f"Real accuracy: "
            f"{real_correct}/{len(real_scores)}"
        )

        print(
            f"AI accuracy: "
            f"{ai_correct}/{len(ai_scores)}"
        )

        print(
            f"Overall accuracy: "
            f"{total_correct}/{total_images} "
            f"({100 * total_correct / total_images:.1f}%)"
        )


if __name__ == "__main__":
    main()