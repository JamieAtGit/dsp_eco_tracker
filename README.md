# Eco Impact Estimator

This project predicts and analyzes the environmental impact of consumer products using:

- Machine learning models (Random Forest and XGBoost)
- Real-time Amazon product scraping
- A Chrome extension overlay
- A web-based React interface

---

## Project Structure

| Folder | Purpose |
|--------|---------|
| `backend/`          | Flask backend and machine learning API |
| `frontend/website/` | React website (Home, Learn, Predict) |
| `frontend/extension/` | Chrome extension (popup-based estimator) |
| `common/data/`      | Datasets and shared CSV resources |
| `ml_model/`         | Trained ML models and encoders |
| `scrapers/`         | Amazon product scraper (Selenium + ChromeDriver) |

---

## Installation & Setup

### Backend (Flask API)

```bash
# Clone the repository
git clone <your-repo-url>
cd DSP/

# Create and activate a virtual environment
python -m venv .venv
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Run the Flask app
python -m backend.api.app

# dsp_eco_tracker
An extension and app that uses machine learning to provide awareness to a user about their purchasing decisions
