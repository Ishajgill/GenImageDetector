# GenImageDetector – FastAPI Backend

A web backend useful to estimate the likelihood that an image is AI-generated
or real. Uploaded images are analyzed by multiple classifiers, and the results
are aggregated into a final confidence score.

---

## Requirements

- **Miniconda or Anaconda** - [Download Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/main)
- **Python 3.13** (installed via conda environment)

**First-time setup:** Initialize conda for your shell, then restart your terminal:

```sh
conda init
```

---

## Development

```sh
# Create a conda environment with Python 3.13
conda create -n gid python=3.13

# Activate the environment
conda activate gid

# Install dependencies
pip install -r requirements.txt

# Run the development server
uvicorn main:app --reload
```
