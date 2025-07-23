# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DSP Eco Tracker is an environmental impact assessment system for Amazon products. Users input Amazon product URLs and their postcode to calculate carbon emissions. The system combines web scraping, machine learning, and geographic analysis.

**Current Grade: 55-58% | Target: 95%**

## Core System Components

### 1. Website (React Frontend)
**Main user flow**: User enters Amazon URL → system scrapes product data → calculates emissions based on user postcode → displays detailed impact assessment

**Key Pages**:
- **HomePage**: Amazon URL + postcode input for emission estimation  
- **PredictPage**: Manual ML model testing interface
- **LearnPage**: Educational content about environmental impact methodology
- **AdminPage**: Review scraped submissions and data quality
- **Login/Signup**: Secure user authentication with role-based access

### 2. Chrome Extension (Two Components)
- **Environmental Tracker**: Same URL + postcode analysis as website
- **Material Tooltip**: Hovers over Amazon product titles showing material type, recyclability, and confidence scores

### 3. Backend ML Pipeline
- **Primary Model**: XGBoost (11 features, ~85.8% accuracy)
- **Fallback Model**: Random Forest (6 features baseline)
- **Dual Validation**: Shows both ML and rule-based predictions side-by-side

## Technology Stack

- **Backend**: Flask with XGBoost/scikit-learn, Selenium for scraping
- **Frontend**: React 18.2.0 with Vite, Chakra UI, Tailwind CSS, Framer Motion
- **Extension**: Chrome Manifest V3 with content scripts and tooltips
- **Development**: Localhost only (no Docker/cloud deployment currently)

## Development Commands

### Backend Setup
```bash
# Virtual environment setup
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
pip install -r backend/requirements.txt

# Run Flask development server (main API)
python backend/api/app.py

# Alternative scraping script
python backend/scrapers/amazon/scrape_amazon_titles.py
```

### Frontend Development
```bash
# Website development
cd frontend/website
npm install
npm run dev        # Development server at http://localhost:5173

# Chrome extension development  
cd frontend/extension
npm install
npm run build      # Build extension for Chrome installation
```

### Machine Learning Training
```bash
# Primary XGBoost model (11 enhanced features)
cd backend/ml/training
python train_xgboost.py

# Fallback Random Forest model (6 baseline features)
python train_model.py

# Data processing pipeline
cd backend/data/processing
python clean_scraped_data.py     # Clean and validate scraped data
python feature_enhancer.py       # Add enhanced ML features
python clean_dataset.py          # Final dataset preparation
```

## Architecture Deep Dive

### Data Processing Pipeline
1. **Product Scraping**: Amazon URL → extract title, price, weight, dimensions, brand, ASIN, origin, materials
2. **Geographic Resolution**: Brand → origin country via `brand_locations.json`
3. **Distance Calculation**: Origin country → user postcode → transport mode selection
4. **Material Detection**: Product title/description → material type with confidence
5. **ML Prediction**: Enhanced features → XGBoost model → emission estimate
6. **Data Storage**: Validated products → `expanded_eco_dataset.csv`

### Key Data Files

#### JSON Data Files
- **`brand_locations.json`**: Brand → origin country mapping (900+ brands) , This helps with quick estimation of products, if a product does not have an origin displayed then we can go to brand locations and get that information that way
- **`cleaned_products.json`**: Validated scraped product data
- **`scraped_products_tmp.json`**: Temporary scraping storage

#### CSV Data Files  
- **`expanded_eco_dataset.csv`**: Main training dataset with all features
- **`defra_material_intensity.csv`**: Official CO2 intensity lookup table
- **`batch_predictions_output.csv`**: ML model prediction results
- **`real_scraped_data.csv`**: Live Amazon scraping results

### ML Feature Engineering

#### Core Features (6)
- Material type (encoded) - Primary material classification
- Transport mode (encoded) - Distance-based: truck/ship/air
- Recyclability (encoded) - Material recyclability assessment  
- Origin country (encoded) - Manufacturing source location
- Weight (log-transformed) - Product weight normalization
- Weight category (binned) - Light/medium/heavy classification

#### Enhanced Features (5)
- Packaging type - Primary/secondary/minimal packaging
- Size category - Small/medium/large physical size
- Quality level - Budget/standard/premium classification
- Pack size - Single/multi-pack detection
- Material confidence - ML confidence in material detection

### Transport & Distance Logic
```python
# Distance-based transport mode selection
if distance < 1500km: transport = "truck" (0.15 kg CO2/kg·km)
elif distance < 6000km: transport = "ship" (0.03 kg CO2/kg·km)  
else: transport = "air" (0.5 kg CO2/kg·km)

# Final emission = material_intensity + (weight × distance × transport_factor)
```

### Core API Endpoints
- **`/estimate_emissions`**: Main product analysis (URL + postcode input)
- **`/predict`**: Direct ML model prediction
- **`/insights`**: Analytics dashboard data  
- **`/admin/submissions`**: Admin review interface

### File Structure Navigation

#### Backend Core
- **`backend/api/app.py`**: Main Flask application and API routes
- **`backend/ml/training/train_xgboost.py`**: Primary XGBoost model training
- **`backend/ml/training/train_model.py`**: Fallback Random Forest training
- **`backend/scrapers/amazon/scrape_amazon_titles.py`**: Amazon product scraping

#### Frontend Core  
- **`frontend/website/src/pages/HomePage.jsx`**: Main URL input interface
- **`frontend/website/src/components/ProductImpactCard.jsx`**: Results display
- **`frontend/extension/src/popup.js`**: Extension environmental tracker
- **`frontend/extension/src/components/tooltip.js`**: Material detection tooltip

#### Data Processing
- **`backend/data/processing/clean_scraped_data.py`**: Data validation pipeline
- **`backend/data/processing/feature_enhancer.py`**: ML feature generation
- **`common/data/csv/expanded_eco_dataset.csv`**: Main training dataset

## Critical Issues (Blocking 95% Grade)

### 🚨 Architecture Debt
- **14 competing scrapers** (need 1 production scraper)
- **3 duplicate Flask apps** (app.py, app_corrected.py, app_enhanced.py)
- **Import errors throughout** - missing __init__.py files
- **0.1% test coverage** - only 1 test file exists

### 🚨 Data Quality Issues  
- Scrapers return "Unknown" for most fields
- No data validation pipeline
- No confidence scoring on extracted data
- No fallback mechanisms

### 🚨 Engineering Practices
- **No CI/CD pipeline**
- **Hardcoded secrets** in code
- **No error handling** - cascade failures
- **No logging framework**
- **No type checking or linting**

## Academic Project Context (DSP Module UFCFXK-30-3)

### Assessment Structure (Total: 100%)
- **Project Report (50%)**: 6000-8000 words + background chapter
- **Viva Demonstration (25%)**: 20-min presentation + 10-min Q&A  
- **Project in Progress (25%)**: Poster, video demo, background chapter (2000-3000 words)

### Report Structure Requirements
1. **Introduction**: Clear aims and objectives for emission prediction system
2. **Literature Review/Background**: Environmental impact assessment methods, ML approaches, web scraping techniques (2000-3000 words, marked separately)
3. **Requirements**: Minimum 10 functional + 10 non-functional requirements
4. **Methodology**: Agile development with iterative ML model improvement
5. **Design**: System architecture, ML pipeline design, database design, UI/UX design
6. **Implementation**: Web scraping, ML training, frontend development, extension development
7. **Testing**: ML model evaluation, user acceptance testing, cross-browser compatibility
8. **Evaluation**: Critical analysis of dual prediction approach, limitations, further work

### Key Success Criteria Alignment
- **Software Development Focus (50-60%)**: ✅ Web scraping, ML pipeline, React frontend, Chrome extension
- **Tangible Software Product**: ✅ Working website + extension + ML models
- **Real-world Problem**: ✅ Environmental sustainability for consumer products
- **Innovation/Creativity**: ✅ Dual prediction system (ML vs rule-based), geographic-aware transport calculation
- **Critical Evaluation**: ✅ Comparison framework between approaches, confidence scoring

### Academic Strengths of DSP Eco Tracker
1. **Technical Complexity**: Multi-component system with ML, web scraping, geographic analysis
2. **Research Depth**: Environmental impact assessment, ML feature engineering, transport emissions
3. **Practical Application**: Real Amazon product analysis with user-specific calculations
4. **Innovation**: Novel combination of ML and rule-based methods with dual validation
5. **Scalability**: Modular architecture supporting dataset expansion and model improvement

### Development Priorities for Academic Success

#### Phase 1: Foundation & Documentation (Current) 
- **Strengthen Literature Review**: Environmental LCA methods, ML in sustainability, carbon footprint calculation standards
- **Formalize Requirements**: Document all functional/non-functional requirements with MoSCoW prioritization
- **System Architecture Documentation**: High-level and low-level design diagrams (class, sequence, deployment)
- **ML Model Validation**: Comprehensive testing framework with cross-validation and performance metrics

#### Phase 2: Implementation Excellence
- **Code Quality**: Comprehensive commenting, error handling, logging throughout system
- **Testing Framework**: Unit tests for ML pipeline, integration tests for API endpoints, user acceptance testing
- **Performance Optimization**: ML model efficiency, web scraping reliability, database query optimization  
- **User Experience**: Intuitive interfaces with clear feedback and confidence indicators

#### Phase 3: Critical Analysis & Evaluation
- **Comparative Analysis**: Detailed ML vs rule-based performance comparison with statistical significance
- **Limitation Analysis**: Model constraints, data quality issues, geographical coverage gaps
- **Future Work**: Automated retraining, expanded material database, real-time product monitoring
- **Reflection**: Development process evaluation, methodology effectiveness, lessons learned

### Demonstration Strategy for Viva
1. **System Overview** (5 min): Architecture walkthrough with live system
2. **Core Functionality Demo** (10 min): Amazon URL → emission calculation → results display
3. **Technical Deep Dive** (5 min): ML model insights, feature engineering, confidence scoring
4. **Q&A Preparation**: ML mathematics, system design decisions, scalability considerations

## 🎯 IMMEDIATE ACTION PLAN: 55% → 95%

### PHASE 1: CRITICAL FIXES (Week 1) - Impact: +20 marks

```bash
# DAY 1-2: Architecture Cleanup
□ Delete 13 redundant scrapers (keep only unified_scraper.py)
□ Delete app_corrected.py and app_enhanced.py (keep only app.py)
□ Fix all imports - create proper __init__.py files
□ Remove ALL hardcoded secrets → use .env file

# DAY 3-4: Fix Data Extraction  
□ Test unified_scraper.py with 10 real Amazon URLs
□ Fix extraction to get ACTUAL data (not "Unknown")
□ Add fallback mechanisms for failed extractions
□ Implement confidence scoring for each field

# DAY 5: Basic Testing
□ Set up pytest infrastructure
□ Write tests for unified_scraper.py
□ Add GitHub Actions CI/CD pipeline
□ Target: 30% test coverage
```

### PHASE 2: ENGINEERING EXCELLENCE (Week 2-3) - Impact: +15 marks

```python
# Testing Framework (Target: 80% coverage)
backend/tests/
├── unit/
│   ├── test_scrapers.py
│   ├── test_ml_models.py  
│   └── test_api_routes.py
├── integration/
│   └── test_full_pipeline.py
└── e2e/
    └── test_user_flows.py

# Error Handling Pattern
class ScrapingService:
    def scrape_with_fallback(self, url: str) -> ProductData:
        try:
            return self.primary_scraper.scrape(url)
        except ScrapingException:
            logger.warning(f"Primary scraper failed for {url}")
            return self.fallback_scraper.scrape(url)
```

### PHASE 3: ML RIGOR (Week 4) - Impact: +10 marks

```python
# Current: Basic training with no validation
# Target: Statistical rigor

class MLPipeline:
    def train_with_validation(self):
        # 1. K-fold cross-validation
        scores = cross_val_score(model, X, y, cv=10)
        print(f"CV Score: {scores.mean():.3f} (+/- {scores.std() * 2:.3f})")
        
        # 2. Statistical significance test
        mcnemar_test(model_a, model_b)
        
        # 3. Bias detection
        bias_metrics = check_bias_across_categories(model, X_test, y_test)
```

### PHASE 4: PRODUCTION READY (Week 5-6) - Impact: +10 marks

```yaml
# .github/workflows/ci.yml
name: CI Pipeline
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Tests
        run: |
          pytest --cov=backend --cov-report=xml
      - name: Upload Coverage
        uses: codecov/codecov-action@v3
```

## 📋 DAILY CHECKLIST

### Today's Critical Tasks
1. [ ] Delete redundant scrapers (keep unified_scraper.py)
2. [ ] Fix imports with __init__.py files
3. [ ] Test scraper with real URLs - verify it works
4. [ ] Remove hardcoded secrets → .env file
5. [ ] Set up basic pytest

### Success Criteria
- ✅ Only 1 scraper in codebase
- ✅ No import errors when running app.py
- ✅ Scraper returns real data (not "Unknown")
- ✅ Tests can run with `pytest`
- ✅ No secrets in git history

## 🚀 Commands to Run Right Now

```bash
# 1. Clean up scrapers
cd backend/scrapers/amazon
mkdir archive
mv *.py archive/  # Move all scrapers
mv archive/unified_scraper.py .  # Keep only unified

# 2. Fix imports
touch backend/__init__.py
touch backend/scrapers/__init__.py
touch backend/scrapers/amazon/__init__.py
touch backend/ml/__init__.py
touch backend/api/__init__.py

# 3. Test the scraper
python debug_scraper.py  # Create this to test

# 4. Set up testing
pip install pytest pytest-cov pytest-mock
pytest --version

# 5. Create .env file
echo "FLASK_SECRET_KEY=$(openssl rand -hex 32)" > .env
echo "FLASK_ENV=development" >> .env
```

## Key Files to Monitor

### Scraper (Primary Focus)
- `backend/scrapers/amazon/unified_scraper.py` - Main scraper to fix

### Flask API  
- `backend/api/app.py` - Main API (remove duplicates)

### ML Models
- `backend/ml/training/train_xgboost.py` - Add proper validation
- `backend/ml/models/` - Model storage

### Tests (Create These)
- `backend/tests/unit/test_scrapers.py`
- `backend/tests/unit/test_ml_models.py`
- `backend/tests/integration/test_pipeline.py`

## Remember: Engineering Excellence = 95%

The difference between 55% and 95% is not features, it's:
- Clean architecture (1 scraper, not 14)
- 80% test coverage (not 0.1%)
- Proper ML validation (not just accuracy)
- Production engineering (error handling, logging, monitoring)
- Professional practices (CI/CD, code reviews, documentation)