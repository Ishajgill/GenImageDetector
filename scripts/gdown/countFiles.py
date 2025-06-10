import os

def count_and_clean_files(folder_path):
    count = 0
    deleted_files = 0
    for fname in os.listdir(folder_path):
        fpath = os.path.join(folder_path, fname)
        if os.path.isfile(fpath):
            try:
                if os.path.getsize(fpath) == 0:
                    os.remove(fpath)
                    deleted_files += 1
                else:
                    count += 1
            except Exception as e:
                print(f"Error processing {fpath}: {e}")
    return count

def process_datasets(base_dir):
    subfolders = ["train/ai", "train/nature", "val/ai", "val/nature"]
    datasets = [
        "ADM", "BigGAN", "GLIDE", "Midjourney",
        "Stable Diffusion V1.4", "Stable Diffusion V1.5",
        "VQDM", "Wukong"
    ]

    print(f"{'Dataset':<25} {'train/ai':<10} {'train/nature':<15} {'val/ai':<10} {'val/nature':<12}")
    for dataset in datasets:
        counts = []
        for sub in subfolders:
            full_path = os.path.join(base_dir, dataset, sub)
            count = count_and_clean_files(full_path) if os.path.exists(full_path) else 0
            counts.append(str(count))
        print(f"{dataset:<25} {counts[0]:<10} {counts[1]:<15} {counts[2]:<10} {counts[3]:<12}")
