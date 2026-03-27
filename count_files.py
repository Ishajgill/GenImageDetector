import os

def count_files_top_level(folder_path):
    return sum(os.path.isfile(os.path.join(folder_path, f)) for f in os.listdir(folder_path))

# Example usage
folder = "/path/to/folder"
print(f"Number of files (top-level only): {count_files_top_level(folder)}")
