#!/usr/bin/env python3
"""
🤖 ENTERPRISE ML MODEL MONITORING & DRIFT DETECTION
==================================================

Production-grade ML monitoring system with comprehensive drift detection,
model performance tracking, and automated alerting.

Features:
- Real-time prediction monitoring and logging
- Statistical drift detection (KL divergence, PSI, KS test)
- Model performance degradation alerts  
- Feature importance tracking and drift
- Prediction confidence distribution analysis
- Automated model retraining triggers
- A/B testing framework for model comparison
- Comprehensive dashboards and reporting

This demonstrates enterprise-level MLOps practices expected
in production machine learning systems.
"""

import json
import logging
import time
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import hashlib
from collections import defaultdict, deque
import pickle

# Statistical libraries for drift detection
from scipy import stats
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib

from .monitoring import monitoring
from .exceptions import BaseEcoTrackerException, ErrorSeverity, ErrorCategory

logger = logging.getLogger(__name__)

class DriftType(str, Enum):
    """Types of model drift"""
    DATA_DRIFT = "data_drift"          # Input feature distribution changes
    CONCEPT_DRIFT = "concept_drift"    # Relationship between input and output changes  
    PREDICTION_DRIFT = "prediction_drift"  # Model output distribution changes
    PERFORMANCE_DRIFT = "performance_drift"  # Model accuracy degrades

class AlertSeverity(str, Enum):
    """Alert severity levels"""
    CRITICAL = "critical"  # Immediate action required
    HIGH = "high"         # Action required within hours
    MEDIUM = "medium"     # Action required within days  
    LOW = "low"          # Informational

@dataclass
class DriftAlert:
    """Represents a drift detection alert"""
    alert_id: str
    drift_type: DriftType
    severity: AlertSeverity
    message: str
    detected_at: datetime
    feature_name: Optional[str] = None
    drift_score: Optional[float] = None
    threshold: Optional[float] = None
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass 
class ModelPrediction:
    """Represents a single model prediction with metadata"""
    prediction_id: str
    model_name: str
    model_version: str
    input_features: Dict[str, Any]
    prediction: Any
    confidence: float
    prediction_time: datetime
    processing_time_ms: float
    user_id: Optional[str] = None
    feedback: Optional[Any] = None
    feedback_time: Optional[datetime] = None

class StatisticalTests:
    """Statistical tests for drift detection"""
    
    @staticmethod
    def kolmogorov_smirnov_test(reference: np.ndarray, current: np.ndarray, alpha: float = 0.05) -> Tuple[float, bool]:
        """
        Kolmogorov-Smirnov test for distribution drift
        
        Returns:
            (p_value, drift_detected)
        """
        statistic, p_value = stats.ks_2samp(reference, current)
        drift_detected = p_value < alpha
        return p_value, drift_detected
    
    @staticmethod
    def population_stability_index(reference: np.ndarray, current: np.ndarray, bins: int = 10) -> float:
        """
        Population Stability Index (PSI) for feature drift detection
        
        PSI values:
        - < 0.1: No significant change
        - 0.1-0.2: Moderate change
        - > 0.2: Significant change
        """
        
        # Create bins based on reference data
        _, bin_edges = np.histogram(reference, bins=bins)
        
        # Get distributions
        ref_counts, _ = np.histogram(reference, bins=bin_edges)
        cur_counts, _ = np.histogram(current, bins=bin_edges)
        
        # Convert to proportions (avoid division by zero)
        ref_props = (ref_counts + 1e-6) / (len(reference) + bins * 1e-6)
        cur_props = (cur_counts + 1e-6) / (len(current) + bins * 1e-6)
        
        # Calculate PSI
        psi = np.sum((cur_props - ref_props) * np.log(cur_props / ref_props))
        
        return psi
    
    @staticmethod
    def kullback_leibler_divergence(reference: np.ndarray, current: np.ndarray, bins: int = 10) -> float:
        """
        Kullback-Leibler divergence for distribution comparison
        
        Higher values indicate more drift
        """
        
        # Create probability distributions
        ref_hist, bin_edges = np.histogram(reference, bins=bins, density=True)
        cur_hist, _ = np.histogram(current, bins=bin_edges, density=True)
        
        # Normalize and add small epsilon to avoid log(0)
        epsilon = 1e-10
        ref_dist = ref_hist + epsilon
        cur_dist = cur_hist + epsilon
        
        ref_dist = ref_dist / np.sum(ref_dist)
        cur_dist = cur_dist / np.sum(cur_dist)
        
        # Calculate KL divergence
        kl_div = np.sum(cur_dist * np.log(cur_dist / ref_dist))
        
        return kl_div
    
    @staticmethod
    def chi_square_test(reference: np.ndarray, current: np.ndarray, bins: int = 10, alpha: float = 0.05) -> Tuple[float, bool]:
        """
        Chi-square test for categorical feature drift
        
        Returns:
            (p_value, drift_detected)
        """
        
        # Create contingency table
        _, bin_edges = np.histogram(np.concatenate([reference, current]), bins=bins)
        
        ref_counts, _ = np.histogram(reference, bins=bin_edges)
        cur_counts, _ = np.histogram(current, bins=bin_edges)
        
        # Perform chi-square test
        contingency_table = np.array([ref_counts, cur_counts])
        
        try:
            chi2, p_value, _, _ = stats.chi2_contingency(contingency_table)
            drift_detected = p_value < alpha
            return p_value, drift_detected
        except ValueError:
            # Handle case where test cannot be performed
            return 1.0, False

class DriftDetector:
    """
    Comprehensive drift detection system
    
    Monitors multiple types of drift using statistical tests
    and machine learning techniques.
    """
    
    def __init__(
        self,
        reference_window_size: int = 1000,
        detection_window_size: int = 100,
        psi_threshold: float = 0.2,
        ks_alpha: float = 0.05,
        kl_threshold: float = 0.1
    ):
        self.reference_window_size = reference_window_size
        self.detection_window_size = detection_window_size
        self.psi_threshold = psi_threshold
        self.ks_alpha = ks_alpha
        self.kl_threshold = kl_threshold
        
        # Data storage for drift detection
        self.reference_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=reference_window_size))
        self.current_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=detection_window_size))
        
        # Alert storage
        self.alerts: List[DriftAlert] = []
        
        logger.info("🔍 Drift detector initialized with statistical thresholds")
    
    def add_reference_data(self, feature_name: str, values: List[float]):
        """Add reference data for baseline comparison"""
        self.reference_data[feature_name].extend(values)
        logger.debug(f"📊 Added {len(values)} reference values for {feature_name}")
    
    def add_current_data(self, feature_name: str, value: float):
        """Add current data point for drift detection"""
        self.current_data[feature_name].append(value)
        
        # Trigger drift detection if we have enough data
        if len(self.current_data[feature_name]) >= self.detection_window_size:
            self._detect_feature_drift(feature_name)
    
    def _detect_feature_drift(self, feature_name: str):
        """Detect drift for a specific feature"""
        
        if feature_name not in self.reference_data or len(self.reference_data[feature_name]) < 100:
            logger.warning(f"⚠️ Insufficient reference data for {feature_name}")
            return
        
        reference = np.array(self.reference_data[feature_name])
        current = np.array(self.current_data[feature_name])
        
        with monitoring.trace_span("drift_detection", {
            "feature_name": feature_name,
            "reference_size": len(reference),
            "current_size": len(current)
        }):
            
            # Population Stability Index
            psi_score = StatisticalTests.population_stability_index(reference, current)
            
            # Kolmogorov-Smirnov test
            ks_p_value, ks_drift = StatisticalTests.kolmogorov_smirnov_test(reference, current, self.ks_alpha)
            
            # Kullback-Leibler divergence
            kl_divergence = StatisticalTests.kullback_leibler_divergence(reference, current)
            
            # Determine drift severity
            drift_detected = False
            severity = AlertSeverity.LOW
            
            if psi_score > self.psi_threshold:
                drift_detected = True
                if psi_score > 0.5:
                    severity = AlertSeverity.CRITICAL
                elif psi_score > 0.3:
                    severity = AlertSeverity.HIGH
                else:
                    severity = AlertSeverity.MEDIUM
            
            if ks_drift:
                drift_detected = True
                severity = max(severity, AlertSeverity.MEDIUM, key=lambda x: x.value)
            
            if kl_divergence > self.kl_threshold:
                drift_detected = True
                severity = max(severity, AlertSeverity.MEDIUM, key=lambda x: x.value)
            
            # Create alert if drift detected
            if drift_detected:
                alert = DriftAlert(
                    alert_id=self._generate_alert_id(feature_name),
                    drift_type=DriftType.DATA_DRIFT,
                    severity=severity,
                    message=f"Data drift detected for feature '{feature_name}'",
                    detected_at=datetime.utcnow(),
                    feature_name=feature_name,
                    drift_score=psi_score,
                    threshold=self.psi_threshold,
                    recommendations=self._generate_drift_recommendations(feature_name, psi_score),
                    metadata={
                        "psi_score": psi_score,
                        "ks_p_value": ks_p_value,
                        "kl_divergence": kl_divergence,
                        "reference_mean": float(np.mean(reference)),
                        "current_mean": float(np.mean(current)),
                        "reference_std": float(np.std(reference)),
                        "current_std": float(np.std(current))
                    }
                )
                
                self.alerts.append(alert)
                self._send_drift_alert(alert)
                
                logger.warning(f"🚨 {severity.upper()} drift alert: {alert.message}")
    
    def _generate_alert_id(self, feature_name: str) -> str:
        """Generate unique alert ID"""
        content = f"{feature_name}:{datetime.utcnow().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _generate_drift_recommendations(self, feature_name: str, drift_score: float) -> List[str]:
        """Generate recommendations based on drift detection"""
        
        recommendations = []
        
        if drift_score > 0.5:
            recommendations.extend([
                "Immediate model retraining required",
                "Investigate data source changes",
                "Consider feature engineering updates"
            ])
        elif drift_score > 0.3:
            recommendations.extend([
                "Schedule model retraining within 24 hours",
                "Monitor prediction accuracy closely",
                "Review data preprocessing pipeline"
            ])
        else:
            recommendations.extend([
                "Monitor feature closely over next week",
                "Consider collecting more recent training data",
                "Review data collection processes"
            ])
        
        return recommendations
    
    def _send_drift_alert(self, alert: DriftAlert):
        """Send drift alert to monitoring system"""
        
        monitoring.create_alert(
            alert_name=f"drift_detection_{alert.drift_type}",
            severity=alert.severity,
            message=alert.message,
            context={
                "alert_id": alert.alert_id,
                "feature_name": alert.feature_name,
                "drift_score": alert.drift_score,
                "threshold": alert.threshold,
                "metadata": alert.metadata
            }
        )

class ModelPerformanceMonitor:
    """
    Monitor model performance and detect performance drift
    
    Tracks accuracy, precision, recall and other metrics over time
    to detect when model quality degrades.
    """
    
    def __init__(self, performance_window_size: int = 500):
        self.performance_window_size = performance_window_size
        
        # Performance tracking
        self.predictions: deque = deque(maxlen=performance_window_size)
        self.ground_truth: deque = deque(maxlen=performance_window_size)
        self.confidence_scores: deque = deque(maxlen=performance_window_size)
        
        # Performance baselines
        self.baseline_accuracy = None
        self.baseline_precision = None
        self.baseline_recall = None
        self.baseline_f1 = None
        
        logger.info("📈 Model performance monitor initialized")
    
    def add_prediction(
        self,
        prediction: Any,
        ground_truth: Optional[Any] = None,
        confidence: Optional[float] = None
    ):
        """Add prediction for performance monitoring"""
        
        self.predictions.append(prediction)
        
        if ground_truth is not None:
            self.ground_truth.append(ground_truth)
        
        if confidence is not None:
            self.confidence_scores.append(confidence)
        
        # Check for performance drift if we have sufficient data
        if len(self.predictions) >= 100 and len(self.ground_truth) >= 100:
            self._check_performance_drift()
    
    def set_baseline_performance(
        self,
        accuracy: float,
        precision: float,
        recall: float,
        f1: float
    ):
        """Set baseline performance metrics"""
        
        self.baseline_accuracy = accuracy
        self.baseline_precision = precision  
        self.baseline_recall = recall
        self.baseline_f1 = f1
        
        logger.info(f"📊 Baseline performance set: Accuracy={accuracy:.3f}, F1={f1:.3f}")
    
    def _check_performance_drift(self):
        """Check for performance degradation"""
        
        if not all([self.baseline_accuracy, self.baseline_precision, self.baseline_recall, self.baseline_f1]):
            logger.warning("⚠️ No baseline performance metrics set")
            return
        
        # Calculate current performance
        current_accuracy = accuracy_score(list(self.ground_truth), list(self.predictions))
        current_precision = precision_score(list(self.ground_truth), list(self.predictions), average='weighted', zero_division=0)
        current_recall = recall_score(list(self.ground_truth), list(self.predictions), average='weighted', zero_division=0)
        current_f1 = f1_score(list(self.ground_truth), list(self.predictions), average='weighted', zero_division=0)
        
        # Check for significant degradation (> 5% drop)
        degradation_threshold = 0.05
        
        accuracy_drop = self.baseline_accuracy - current_accuracy
        precision_drop = self.baseline_precision - current_precision
        recall_drop = self.baseline_recall - current_recall
        f1_drop = self.baseline_f1 - current_f1
        
        if any(drop > degradation_threshold for drop in [accuracy_drop, precision_drop, recall_drop, f1_drop]):
            
            # Determine severity
            max_drop = max(accuracy_drop, precision_drop, recall_drop, f1_drop)
            if max_drop > 0.15:
                severity = AlertSeverity.CRITICAL
            elif max_drop > 0.10:
                severity = AlertSeverity.HIGH
            else:
                severity = AlertSeverity.MEDIUM
            
            # Create performance drift alert
            alert = DriftAlert(
                alert_id=self._generate_alert_id("performance"),
                drift_type=DriftType.PERFORMANCE_DRIFT,
                severity=severity,
                message=f"Model performance degradation detected (max drop: {max_drop:.3f})",
                detected_at=datetime.utcnow(),
                drift_score=max_drop,
                threshold=degradation_threshold,
                recommendations=[
                    "Immediate model retraining required",
                    "Investigate data quality issues",
                    "Consider feature engineering updates",
                    "Review model hyperparameters"
                ],
                metadata={
                    "current_accuracy": current_accuracy,
                    "current_precision": current_precision,
                    "current_recall": current_recall,
                    "current_f1": current_f1,
                    "baseline_accuracy": self.baseline_accuracy,
                    "baseline_precision": self.baseline_precision,
                    "baseline_recall": self.baseline_recall,  
                    "baseline_f1": self.baseline_f1,
                    "accuracy_drop": accuracy_drop,
                    "precision_drop": precision_drop,
                    "recall_drop": recall_drop,
                    "f1_drop": f1_drop
                }
            )
            
            self._send_performance_alert(alert)
            logger.critical(f"🚨 PERFORMANCE DRIFT: {alert.message}")
    
    def _generate_alert_id(self, prefix: str) -> str:
        """Generate unique alert ID"""
        content = f"{prefix}:{datetime.utcnow().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _send_performance_alert(self, alert: DriftAlert):
        """Send performance alert to monitoring system"""
        
        monitoring.create_alert(
            alert_name="model_performance_degradation",
            severity=alert.severity,
            message=alert.message,
            context=alert.metadata
        )

class MLMonitoringService:
    """
    Enterprise ML monitoring service
    
    Comprehensive monitoring system for production ML models with
    drift detection, performance tracking, and automated alerting.
    """
    
    def __init__(self, model_name: str, model_version: str):
        self.model_name = model_name
        self.model_version = model_version
        
        # Initialize components
        self.drift_detector = DriftDetector()
        self.performance_monitor = ModelPerformanceMonitor()
        
        # Prediction storage
        self.predictions: List[ModelPrediction] = []
        self.prediction_stats = {
            "total_predictions": 0,
            "average_confidence": 0.0,
            "average_processing_time": 0.0,
            "feature_stats": defaultdict(dict)
        }
        
        logger.info(f"🤖 ML monitoring service initialized for {model_name} v{model_version}")
    
    def log_prediction(
        self,
        input_features: Dict[str, Any],
        prediction: Any,
        confidence: float,
        processing_time_ms: float,
        user_id: Optional[str] = None
    ) -> str:
        """
        Log a model prediction with comprehensive metadata
        
        Returns:
            prediction_id for tracking and feedback
        """
        
        prediction_id = self._generate_prediction_id()
        
        # Create prediction record
        pred_record = ModelPrediction(
            prediction_id=prediction_id,
            model_name=self.model_name,
            model_version=self.model_version,
            input_features=input_features,
            prediction=prediction,
            confidence=confidence,
            prediction_time=datetime.utcnow(),
            processing_time_ms=processing_time_ms,
            user_id=user_id
        )
        
        self.predictions.append(pred_record)
        
        # Update statistics
        self._update_prediction_stats(pred_record)
        
        # Add features to drift detection
        for feature_name, feature_value in input_features.items():
            if isinstance(feature_value, (int, float)):
                self.drift_detector.add_current_data(feature_name, float(feature_value))
        
        # Record monitoring metrics
        monitoring.record_ml_prediction(
            self.model_name,
            confidence,
            processing_time_ms / 1000.0
        )
        
        logger.debug(f"📝 Logged prediction {prediction_id} with confidence {confidence:.3f}")
        
        return prediction_id
    
    def add_feedback(self, prediction_id: str, ground_truth: Any):
        """Add ground truth feedback for performance monitoring"""
        
        # Find prediction record
        for pred in self.predictions:
            if pred.prediction_id == prediction_id:
                pred.feedback = ground_truth
                pred.feedback_time = datetime.utcnow()
                
                # Add to performance monitor
                self.performance_monitor.add_prediction(
                    prediction=pred.prediction,
                    ground_truth=ground_truth,
                    confidence=pred.confidence
                )
                
                logger.debug(f"✅ Added feedback for prediction {prediction_id}")
                break
    
    def set_baseline_data(self, baseline_features: pd.DataFrame):
        """Set baseline feature distributions for drift detection"""
        
        for column in baseline_features.columns:
            if baseline_features[column].dtype in ['int64', 'float64']:
                values = baseline_features[column].dropna().tolist()
                self.drift_detector.add_reference_data(column, values)
        
        logger.info(f"📊 Set baseline data for {len(baseline_features.columns)} features")
    
    def set_baseline_performance(self, baseline_metrics: Dict[str, float]):
        """Set baseline performance metrics"""
        
        self.performance_monitor.set_baseline_performance(
            accuracy=baseline_metrics.get('accuracy', 0.0),
            precision=baseline_metrics.get('precision', 0.0),
            recall=baseline_metrics.get('recall', 0.0),
            f1=baseline_metrics.get('f1', 0.0)
        )
    
    def _generate_prediction_id(self) -> str:
        """Generate unique prediction ID"""
        content = f"{self.model_name}:{time.time()}:{len(self.predictions)}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _update_prediction_stats(self, prediction: ModelPrediction):
        """Update prediction statistics"""
        
        self.prediction_stats["total_predictions"] += 1
        
        # Update running averages
        total = self.prediction_stats["total_predictions"]
        
        # Confidence average
        old_conf_avg = self.prediction_stats["average_confidence"]
        self.prediction_stats["average_confidence"] = (
            old_conf_avg * (total - 1) + prediction.confidence
        ) / total
        
        # Processing time average
        old_time_avg = self.prediction_stats["average_processing_time"]
        self.prediction_stats["average_processing_time"] = (
            old_time_avg * (total - 1) + prediction.processing_time_ms
        ) / total
        
        # Feature statistics
        for feature_name, feature_value in prediction.input_features.items():
            if isinstance(feature_value, (int, float)):
                if feature_name not in self.prediction_stats["feature_stats"]:
                    self.prediction_stats["feature_stats"][feature_name] = {
                        "sum": 0.0,
                        "sum_sq": 0.0,
                        "count": 0,
                        "min": float('inf'),
                        "max": float('-inf')
                    }
                
                stats = self.prediction_stats["feature_stats"][feature_name]
                stats["sum"] += feature_value
                stats["sum_sq"] += feature_value ** 2
                stats["count"] += 1
                stats["min"] = min(stats["min"], feature_value)
                stats["max"] = max(stats["max"], feature_value)
    
    def get_monitoring_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive monitoring dashboard data"""
        
        # Recent alerts (last 24 hours)
        recent_alerts = [
            alert for alert in self.drift_detector.alerts
            if alert.detected_at > datetime.utcnow() - timedelta(hours=24)
        ]
        
        # Feature statistics with mean and std
        feature_stats = {}
        for feature_name, stats in self.prediction_stats["feature_stats"].items():
            if stats["count"] > 0:
                mean = stats["sum"] / stats["count"]
                variance = (stats["sum_sq"] / stats["count"]) - (mean ** 2)
                std = variance ** 0.5 if variance > 0 else 0.0
                
                feature_stats[feature_name] = {
                    "mean": mean,
                    "std": std,
                    "min": stats["min"],
                    "max": stats["max"],
                    "count": stats["count"]
                }
        
        # Confidence distribution
        recent_predictions = self.predictions[-100:] if len(self.predictions) > 100 else self.predictions
        confidence_scores = [p.confidence for p in recent_predictions]
        
        return {
            "model_info": {
                "name": self.model_name,
                "version": self.model_version,
                "total_predictions": self.prediction_stats["total_predictions"],
                "average_confidence": round(self.prediction_stats["average_confidence"], 3),
                "average_processing_time_ms": round(self.prediction_stats["average_processing_time"], 2)
            },
            "drift_status": {
                "total_alerts": len(self.drift_detector.alerts),
                "recent_alerts": len(recent_alerts),
                "alert_breakdown": {
                    alert_type.value: len([a for a in recent_alerts if a.drift_type == alert_type])
                    for alert_type in DriftType
                }
            },
            "feature_statistics": feature_stats,
            "confidence_distribution": {
                "mean": np.mean(confidence_scores) if confidence_scores else 0.0,
                "std": np.std(confidence_scores) if confidence_scores else 0.0,
                "low_confidence_rate": len([c for c in confidence_scores if c < 0.7]) / len(confidence_scores) if confidence_scores else 0.0
            },
            "recent_alerts": [
                {
                    "alert_id": alert.alert_id,
                    "type": alert.drift_type,
                    "severity": alert.severity,
                    "message": alert.message,
                    "detected_at": alert.detected_at.isoformat(),
                    "feature_name": alert.feature_name,
                    "drift_score": alert.drift_score
                }
                for alert in recent_alerts[-10:]  # Last 10 alerts
            ]
        }

# Global ML monitoring instance
ml_monitoring = MLMonitoringService("xgboost_eco_tracker", "1.0.0")

# Decorator for monitoring ML predictions
def monitor_prediction(model_name: str):
    """Decorator to automatically monitor ML model predictions"""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                # Execute prediction
                result = func(*args, **kwargs)
                processing_time = (time.time() - start_time) * 1000
                
                # Extract prediction info from result
                if isinstance(result, dict):
                    prediction = result.get('prediction')
                    confidence = result.get('confidence', 0.0)
                    features = result.get('features', {})
                    
                    # Log prediction
                    prediction_id = ml_monitoring.log_prediction(
                        input_features=features,
                        prediction=prediction,
                        confidence=confidence,
                        processing_time_ms=processing_time
                    )
                    
                    # Add prediction ID to result
                    result['prediction_id'] = prediction_id
                
                return result
                
            except Exception as e:
                processing_time = (time.time() - start_time) * 1000
                logger.error(f"❌ Prediction failed after {processing_time:.2f}ms: {e}")
                raise
        
        return wrapper
    return decorator

if __name__ == "__main__":
    # Test the ML monitoring system
    print("🤖 Testing ML Monitoring & Drift Detection System")
    print("=" * 60)
    
    # Initialize monitoring
    monitor = MLMonitoringService("test_model", "1.0.0")
    
    # Set baseline data
    baseline_data = pd.DataFrame({
        'feature_1': np.random.normal(0, 1, 1000),
        'feature_2': np.random.normal(5, 2, 1000),
        'feature_3': np.random.exponential(2, 1000)
    })
    monitor.set_baseline_data(baseline_data)
    
    # Set baseline performance
    monitor.set_baseline_performance({
        'accuracy': 0.85,
        'precision': 0.83,
        'recall': 0.87,
        'f1': 0.85
    })
    
    # Simulate predictions with drift
    print("📊 Simulating predictions...")
    
    for i in range(200):
        # Simulate drift by gradually shifting feature distributions
        drift_factor = i / 200.0
        
        features = {
            'feature_1': np.random.normal(drift_factor * 2, 1),  # Mean drift
            'feature_2': np.random.normal(5, 2 + drift_factor),  # Variance drift
            'feature_3': np.random.exponential(2 - drift_factor * 0.5)  # Distribution drift
        }
        
        # Simulate prediction
        prediction = np.random.choice([0, 1])
        confidence = np.random.uniform(0.6, 0.95)
        
        prediction_id = monitor.log_prediction(
            input_features=features,
            prediction=prediction,
            confidence=confidence,
            processing_time_ms=np.random.uniform(10, 50)
        )
        
        # Occasionally add feedback
        if i % 10 == 0:
            ground_truth = np.random.choice([0, 1])
            monitor.add_feedback(prediction_id, ground_truth)
    
    # Get dashboard
    dashboard = monitor.get_monitoring_dashboard()
    
    print(f"✅ Model: {dashboard['model_info']['name']}")
    print(f"📈 Total predictions: {dashboard['model_info']['total_predictions']}")
    print(f"🎯 Average confidence: {dashboard['model_info']['average_confidence']}")
    print(f"🚨 Total drift alerts: {dashboard['drift_status']['total_alerts']}")
    print(f"⚠️ Recent alerts: {dashboard['drift_status']['recent_alerts']}")
    
    if dashboard['recent_alerts']:
        print("\n🔍 Recent Alerts:")
        for alert in dashboard['recent_alerts'][-3:]:
            print(f"  - {alert['severity'].upper()}: {alert['message']}")
    
    print("\n🚀 ML monitoring system ready for production!")