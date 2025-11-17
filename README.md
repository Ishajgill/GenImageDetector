# GenImageDetector

A web application to estimate the likelihood that an image is AI-generated or real. The system analyzes uploaded images using multiple classifiers and aggregates results into a final confidence score.

## Architecture

- **Backend**: FastAPI-based REST API that processes images through multiple AI detection classifiers
- **Frontend**: React + Vite web interface for uploading and analyzing images in the browser

## Requirements

- **Backend**: Python 3.10+
- **Frontend**: Node.js 22+ (install via [nvm](https://github.com/nvm-sh/nvm))

## Quick Start

### Backend

1. Follow the installation steps in [`backend/README.md`](backend/README.md)
2. From the `backend/` directory, start the API server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend

1. Follow the installation steps in [`frontend/README.md`](frontend/README.md)
2. From the `frontend/` directory, start the UI server:
   ```bash
   pnpm run dev
   ```
3. Open your browser to http://localhost:5173

## Project Structure

- `backend/` - FastAPI server with classifier implementations
- `frontend/` - React web interface
- `scripts/` - Dataset download and generation utilities
- `models/` - Trained model files and validation results
