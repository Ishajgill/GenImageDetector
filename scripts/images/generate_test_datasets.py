# generate_images.py
import os
import random
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "random_images")

MAX_DIR = 10
MAX_DEPTH = 3
MAX_IMAGES_PER_FOLDER = 20


def make_random_image(path):
    width, height = random.randint(50, 500), random.randint(50, 500)
    image = Image.new(
        "RGB",
        (width, height),
        (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        ),
    )
    image.save(path, format="JPEG")


def make_corrupt_image(path):
    with open(path, "wb") as f:
        f.write(b"This is not a valid image file.")


def make_empty_file(path):
    open(path, "wb").close()


def create_random_structure(base_path, depth=0):
    if depth > MAX_DEPTH:
        return
    os.makedirs(base_path, exist_ok=True)

    for _ in range(
        random.randint(MAX_IMAGES_PER_FOLDER // 3, MAX_IMAGES_PER_FOLDER)
    ):
        choice = random.choices(
            ["good", "corrupt", "empty"], weights=[0.7, 0.2, 0.1]
        )[0]
        filename = f"img_{random.randint(10000, 99999)}.jpg"
        filepath = os.path.join(base_path, filename)
        if choice == "good":
            make_random_image(filepath)
        elif choice == "corrupt":
            make_corrupt_image(filepath)
        elif choice == "empty":
            make_empty_file(filepath)

    # Create random subfolders.
    for _ in range(random.randint(MAX_DIR // 3, MAX_DIR)):
        subfolder = os.path.join(base_path, f"sub_{random.randint(1000,9999)}")
        create_random_structure(subfolder, depth + 1)


if __name__ == "__main__":
    if os.path.exists(IMG_DIR):
        import shutil

        shutil.rmtree(IMG_DIR)
    create_random_structure(IMG_DIR)
    print(f"Generated image tree under {IMG_DIR}/")
