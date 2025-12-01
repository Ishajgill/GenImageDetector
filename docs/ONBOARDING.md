# GenImageDetector Onboarding Guide

Welcome to the GenImageDetector project! This guide will help you get started whether you're interested in improving the ML models, enhancing the web interface, or exploring AI image detection research.

## Project Overview

GenImageDetector is a full-stack web application that detects AI-generated images using multiple machine learning models. The system provides an intuitive interface for users to upload images and receive detailed confidence scores with visual feedback.

**What makes this project special:**

- Modular architecture that supports multiple detection models
- Real-time analysis with progressive loading and smooth animations
- User authentication with persistent analysis history
- Production-ready web interface built with modern tools

## Getting Started

### Prerequisites

- **Backend**: Python 3.13, Miniconda/Anaconda
- **Frontend**: Node.js 22+
- **Recommended**: Git, VSCode or similar editor

### Quick Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/RyanAIIen/GenImageDetector.git
   cd GenImageDetector
   ```

2. **Set up the backend** (see [`backend/README.md`](backend/README.md))

   ```bash
   cd backend
   conda create -n gid python=3.13
   conda activate gid
   pip install -r requirements.txt
   python -m db.init_db
   python -m db.load_fixtures
   uvicorn main:app --reload
   ```

3. **Set up the frontend** (see [`frontend/README.md`](frontend/README.md))

   ```bash
   cd frontend
   pnpm install
   pnpm run dev
   ```

4. **Access the application**
   - Frontend: http://localhost:5173
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## How to Contribute

### Adding New Detection Models

The system is designed to support additional AI detection models. Currently, we use:

- **CNNSpot**: Trained model for general AI image detection
- **HuggingFace Models**: AI_vs_Human and NYUAD pre-trained classifiers
- **Demo Classifiers**: Placeholder models for testing

**To add a new model:**

1. **Understand the classifier interface** (`backend/ml/classifiers/base.py`)

   ```python
   class YourClassifier:
       def analyze(self, image: PIL.Image, **kwargs) -> float:
           # Return confidence score (0-100)
           # Higher = more likely real
           pass
   ```

2. **Create your classifier class** in `backend/ml/classifiers/`

   - Inherit from an existing base or implement the interface
   - Handle model loading in `__init__`
   - Implement `analyze()` to return 0-100 confidence

3. **Register in the analysis pipeline** (`backend/analysis/routes.py`)

   ```python
   # Initialize your classifier
   your_classifier = YourClassifier("path/to/weights")

   # Add to the results dict
   results = {
       "Your_Model": your_classifier.analyze(img),
       # ... other models
   }
   ```

4. **Optional: Set model-specific threshold** (`frontend/src/utils.ts` and `frontend/src/components/analyzer/Analyzer.tsx`)
   ```typescript
   const MODEL_THRESHOLDS: Record<string, number> = {
     Your_Model: 75, // Adjust based on validation
   };
   ```

### Working with GenImage Models

The [GenImage dataset](https://github.com/GenImage-Dataset/GenImage/) provides training code for various detection models. If you train models using their framework:

1. **Place model weights** in `backend/ml/models/YourModel/`
2. **Create a classifier wrapper** following the CNNSpot example
3. **Configure any preprocessing** needed (crop size, normalization, etc.)
4. **Test thoroughly** with both real and AI-generated images

**Model integration checklist:**

- [ ] Model loads successfully on startup
- [ ] Returns confidence scores in 0-100 range
- [ ] Handles various image sizes and formats
- [ ] Validates performance on test images
- [ ] Documentation updated with model details

### Improving the Web Interface

The frontend is built with React, TypeScript, and Material UI. Key areas for enhancement:

**UX Improvements:**

- Batch image analysis
- Side-by-side comparison mode
- Export analysis reports
- Model performance explanations

**Visualization:**

- Heatmaps showing detection regions
- Confidence trends over time
- Model agreement/disagreement indicators

**Features:**

- Image preprocessing options
- Advanced filtering and search in history
- Sharing analysis results
- Mobile-optimized interface

### Backend Enhancements

**API Features:**

- Batch analysis endpoints
- Webhook notifications for long-running analyses
- Model performance metrics API
- Admin panel for model management

**Performance:**

- Async processing for multiple images
- Result caching
- Model response time optimization
- Database query optimization

**Testing:**

- Unit tests for classifiers
- Integration tests for API endpoints
- Load testing for concurrent users

## Project Structure

```
GenImageDetector/
├── backend/              # FastAPI server
│   ├── ml/              # ML models and classifiers
│   │   ├── classifiers/ # Classifier implementations
│   │   └── models/      # Model weights and configs
│   ├── auth/            # Authentication system
│   ├── analysis/        # Analysis endpoints
│   └── db/              # Database setup and fixtures
├── frontend/            # React web application
│   ├── src/
│   │   ├── components/  # UI components
│   │   ├── contexts/    # Global state
│   │   └── providers/   # Context providers
└── scripts/             # Utility scripts
```

## Development Workflow

1. **Pick an issue** or create one describing what you want to work on
2. **Create a branch** for your feature or fix
3. **Develop and test** locally using the dev servers
4. **Document changes** in code comments and README as needed
5. **Submit a pull request** with clear description of changes

## Tips for Success

**Starting with ML:**

- CNNSpot (`backend/ml/classifiers/cnnspot.py`) is the best reference implementation
- Test new classifiers with known real/AI images before integration
- Model confidence should trend correctly (higher for real images if that's your training)

**Starting with Frontend:**

- Check `Analyzer.tsx` for the main analysis workflow
- Material UI components have great documentation
- State management uses React Context (see `AppContext` and `AuthContext`)

**General:**

- Run the backend API docs at `/docs` to explore endpoints interactively
- Check browser console and terminal output for debugging hints
- Don't hesitate to ask questions in issues or discussions

## Resources

- **API Documentation**: http://localhost:8000/docs (when running)
- **GenImage Dataset**: https://github.com/GenImage-Dataset/GenImage/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React + Material UI**: https://mui.com/material-ui/
- **HuggingFace Transformers**: https://huggingface.co/docs/transformers/

## What's Next?

**High-Impact Contributions:**

- Integrate additional trained GenImage models
- Add model evaluation dashboard
- Implement batch processing
- Create mobile-responsive design improvements
- Add comprehensive test coverage

**Research Directions:**

- Compare detection performance across models
- Analyze failure cases and edge conditions
- Explore ensemble methods beyond weighted average
- Study detection on specific AI tools (Midjourney, DALL-E, etc.)

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions or ideas
- Check existing issues for similar topics

Thank you for your interest in GenImageDetector! We're excited to see where you take this project.
