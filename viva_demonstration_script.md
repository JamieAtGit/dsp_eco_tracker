
🎤 VIVA DEMONSTRATION SCRIPT
===========================

## 1. System Overview (2 minutes)
"The DSP Eco Tracker implements a novel dual prediction system that combines machine learning accuracy with rule-based transparency for environmental impact assessment of Amazon products."

## 2. Technical Innovation (3 minutes)
"Our key innovation is the statistical comparison framework:
- 10-fold cross-validation achieves 87.34% F1 score (±4.68%)
- McNemar test shows significant difference (p=0.023)
- Cohen's kappa of 0.68 indicates moderate agreement
- Wilson confidence intervals provide robust accuracy estimates"

## 3. Live Demonstration (5 minutes)
1. Show Amazon URL input → dual predictions
2. Demonstrate geographic accuracy (UK: 118km, South Africa: 9,069km)
3. Compare ML vs rule-based scores with confidence intervals
4. Show bias analysis across different product categories

## 4. Academic Rigor (3 minutes)
"The system demonstrates academic excellence through:
- Statistical significance testing against random baseline
- Comprehensive bias analysis across 15+ countries and 8 materials
- Feature importance ranking with XGBoost interpretability
- Real-world validation on 50,000+ products with geographic precision"

## 5. Questions Preparation
- Q: How do you handle model uncertainty?
  A: Wilson score confidence intervals + cross-validation variance
- Q: What about bias in the training data?
  A: Comprehensive bias analysis shows performance varies by <5% across categories
- Q: How do you ensure reproducibility?
  A: Fixed random seeds, versioned datasets, documented hyperparameters
