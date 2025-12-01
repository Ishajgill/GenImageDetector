# GenImageDetector

A full-stack web application for detecting AI-generated images. The system analyzes uploaded images using multiple ML classifiers and provides detailed confidence scores with an aggregate verdict.

## Features

### Analysis

- **5 ML Models**: CNNSpot (trained), AI_vs_Human, NYUAD (HuggingFace), and 2 demo classifiers
- **Model-Specific Thresholds**: Each model uses optimized thresholds for accurate verdicts
- **Weighted Aggregation**: Final verdict weighs confident predictions more heavily
- **Visual Results**: Animated gauges, confidence bars, and color-coded verdicts

### User Experience

- **Progressive Loading**: Multi-stage progress indicators with skeleton screens
- **Real-time Analysis**: Immediate feedback with smooth animations
- **Dark/Light Mode**: Theme preference persists across sessions
- **Responsive Design**: Works on desktop and mobile viewports

### History & Authentication

- **User Accounts**: JWT-based authentication with secure password hashing
- **Analysis History**: All analyses saved with timestamps and retrievable by URL
- **Anonymous Mode**: Use without login; history stored in browser
- **Account Migration**: Transfer anonymous history when logging in

## Architecture

- **Backend**: FastAPI REST API with SQLAlchemy ORM and SQLite database
- **Frontend**: React + TypeScript + Material UI with Vite build system
- **Database**: SQLite with UUID primary keys for all entities
- **State Management**: React Context for global state (auth, history, current result)

## Requirements

- **Backend**: Python 3.13, Miniconda/Anaconda
- **Frontend**: Node.js 22+ (install via [nvm](https://github.com/nvm-sh/nvm))

## Quick Start

### Backend

1. Follow the installation steps in [`backend/README.md`](backend/README.md)
2. From the `backend/` directory:

   ```bash
   # Activate conda environment
   conda activate gid

   # Initialize database and load fixtures
   python -m db.init_db
   python -m db.load_fixtures

   # Start the API server
   uvicorn main:app --reload
   ```

3. API will be available at http://localhost:8000
4. API docs at http://localhost:8000/docs

### Frontend

1. Follow the installation steps in [`frontend/README.md`](frontend/README.md)
2. From the `frontend/` directory:
   ```bash
   pnpm run dev
   ```
3. Open your browser to http://localhost:5173

### Default Test Users

| Username | Password |
| -------- | -------- |
| user123  | user123  |
| ryan     | test1234 |

## Project Structure

- `backend/` - FastAPI server with ML classifiers and authentication
  - `ml/` - Classifier implementations (CNNSpot, HuggingFace models)
  - `auth/` - JWT authentication and user management
  - `analysis/` - Image analysis endpoints and history
  - `db/` - Database models, initialization, and fixtures
- `frontend/` - React web interface with Material UI
  - `components/` - Analyzer, Sidebar, Auth dialog
  - `contexts/` - Global state management
  - `providers/` - Context providers for auth and app state
- `scripts/` - Dataset download and generation utilities
- `models/` - Trained model files and validation results
