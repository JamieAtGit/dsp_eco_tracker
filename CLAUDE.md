# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DSP Eco Tracker is a comprehensive environmental impact assessment system for Amazon products. Users input Amazon product URLs and their postcode to get detailed carbon emission calculations. The system combines web scraping, machine learning, geographic analysis, and dual validation (ML vs rule-based) to provide accurate sustainability insights.

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

## Current Development Status

### ✅ Working Components
- Website URL + postcode emission estimation
- XGBoost ML model with 85.8% accuracy
- Amazon product scraping with anti-detection
- Geographic distance calculations  
- Dual prediction comparison (ML vs rule-based)
- Admin interface for data review
- Chrome extension basic functionality

### ⚠️ Partial Implementation
- Extension material tooltips (needs more materials database)
- Brand location database (incomplete coverage)
- Real-time scraping (limited by anti-bot measures)
- User authentication system (basic implementation)

### ❌ Needs Work
- Extension tooltip confidence accuracy
- Automated model retraining pipeline
- Material database expansion for better tooltip coverage
- User session persistence and security hardening

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

## 🚀 Path to 95% Technical Excellence

### Critical Enhancement Areas (Priority Order)

#### 1. **Scraping Accuracy Enhancement** (25 points impact)

**Current Issue**: Scraped data returning "Unknown" instead of actual Amazon product values
**Target**: 95%+ accuracy for origin, weight, material, dimensions extraction

**Enhancement Strategy**:
- **Structured Data Extraction**: Parse Amazon's technical specifications table with multiple fallback selectors
- **Advanced Selenium Patterns**: Implement explicit waits, dynamic content handling, element presence validation
- **Amazon Format Parsing**: Handle all Amazon product detail variations (bullet points, dimensions format, tech specs)
- **Multi-Source Validation**: Cross-validate scraped data against multiple page sections
- **Confidence Scoring**: Track extraction confidence for each field with source attribution

```python
# Enhanced extraction hierarchy:
# 1. Technical specifications table (highest confidence)
# 2. Product details section (high confidence)  
# 3. Feature bullets (medium confidence)
# 4. Product description (low confidence)
# 5. Brand intelligence fallback (medium confidence)
```

#### 2. **ML Model Engineering Rigor** (20 points impact)

**Current**: Basic XGBoost with 85.8% accuracy
**Target**: 90%+ accuracy with statistical validation and uncertainty quantification

**Enhancements**:
- **Cross-Validation Framework**: K-fold CV with statistical significance testing
- **Feature Engineering**: Advanced feature interactions, polynomial features, temporal features
- **Model Uncertainty**: Monte Carlo dropout, prediction intervals, confidence bounds
- **Bias Detection**: Performance analysis across product categories, price ranges, origins
- **Ensemble Methods**: XGBoost + Random Forest + Neural Network voting classifier

#### 3. **Data Quality Pipeline** (15 points impact)

**Current**: Limited validation of scraped data quality
**Target**: Comprehensive data validation with automated quality scoring

**Pipeline Components**:
- **Input Validation**: Amazon URL format validation, product page verification
- **Extraction Validation**: Field completeness scoring, data type verification
- **Cross-Reference Validation**: Brand-origin consistency, weight-dimension correlation
- **Quality Scoring**: Overall confidence metric for each scraped product
- **Automated Cleaning**: Outlier detection, format standardization, duplicate handling

#### 4. **Production-Grade Error Handling** (10 points impact)

**Enhancements**:
- **Graceful Degradation**: Fallback mechanisms when primary extraction fails
- **Retry Logic**: Exponential backoff for failed requests
- **Anti-Bot Resilience**: User-agent rotation, realistic browsing patterns, CAPTCHA handling
- **Structured Logging**: Detailed extraction provenance and error tracking
- **Performance Monitoring**: Scraping success rates, extraction time metrics

### 🎯 Implementation Priority Queue

#### **Week 1-2: Core Scraping Enhancement**
1. **Enhanced Structured Data Extraction** - Fix weight/origin/material extraction accuracy
2. **Advanced Selenium Patterns** - Robust element detection and dynamic content handling  
3. **Amazon Format Parser** - Handle all product detail table variations
4. **Multi-Source Validation** - Cross-validate extracted data for consistency

#### **Week 3-4: ML Engineering Excellence** 
1. **Cross-Validation Framework** - Proper statistical validation of model performance
2. **Feature Engineering Pipeline** - Advanced feature interactions and transformations
3. **Model Uncertainty Quantification** - Prediction intervals and confidence bounds
4. **Ensemble Methods** - Multi-model voting for improved accuracy

#### **Week 5-6: System Integration & Testing**
1. **Comprehensive Testing Framework** - Unit, integration, and E2E tests
2. **Data Quality Pipeline** - Automated validation and quality scoring
3. **Performance Optimization** - Scraping speed, ML inference optimization
4. **Production Error Handling** - Robust fault tolerance and monitoring

### 📊 Success Metrics for 95% Grade

**Technical Metrics**:
- Scraping accuracy: 95%+ for origin, weight, material extraction
- ML model accuracy: 90%+ with proper cross-validation
- Data completeness: <5% "Unknown" values in final dataset
- System reliability: 99%+ uptime with graceful error handling

**Academic Metrics**:
- Code quality: Comprehensive documentation, testing, error handling
- Innovation: Novel dual validation approach with statistical comparison
- Rigor: Proper ML validation, bias detection, uncertainty quantification
- Impact: Real-world applicability with measurable environmental benefit

### 🔧 Key Technical Files to Enhance

#### **Scraping Core** (`backend/scrapers/amazon/`)
- `scrape_amazon_titles.py` - Main scraping logic enhancement
- `structured_extraction.py` - New: Amazon format parsing
- `validation_pipeline.py` - New: Data quality validation

#### **ML Pipeline** (`backend/ml/`)
- `train_xgboost.py` - Enhanced with cross-validation and uncertainty
- `feature_engineering.py` - Advanced feature pipeline
- `model_evaluation.py` - New: Comprehensive evaluation framework

#### **Data Processing** (`backend/data/processing/`)
- `enhanced_cleaning.py` - New: Advanced data cleaning with quality scoring
- `validation_engine.py` - New: Multi-source data validation
- `confidence_tracker.py` - New: Extraction confidence monitoring

### 💡 Innovation Highlights for Academic Excellence

1. **Dual Validation Framework**: Statistical comparison of ML vs rule-based predictions
2. **Confidence-Aware Extraction**: Source attribution and reliability scoring for all data
3. **Global Logistics Modeling**: Distance-based transport mode selection with real-world accuracy
4. **Compound Material Analysis**: Multi-material recyclability assessment
5. **Context-Aware Brand Intelligence**: Product-specific manufacturing pattern detection

This roadmap positions your project for 95% by addressing the core technical deficiencies while maintaining the strong academic foundation you've already built.