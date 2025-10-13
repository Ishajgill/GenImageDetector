# GenImageDetector – FastAPI Backend

A web backend useful to estimate the likelihood that an image is AI-generated
or real. Uploaded images are analyzed by multiple classifiers, and the results
are aggregated into a final confidence score.

---

## Requirements

- Python 3.10+

---

## Development

```sh
# Create the virtual environment
python -m venv venv

# Activate the virtual environment:
# in Linux & macOS
. venv/bin/activate
# or Windows
.\venv\Scripts\activate.bat

# Install the dependencies
pip install -r requirements.txt

# Run the app
uvicorn main:app --reload
```
