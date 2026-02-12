"""
Machine Learning Phishing Detector
Trained on URL features to classify phishing vs legitimate websites
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


class PhishingDetector:
    """
    ML-based phishing detection system
    Analyzes URL features and returns phishing probability
    """
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.model_path = Path(__file__).parent / "phishing_model.pkl"
        self.scaler_path = Path(__file__).parent / "scaler.pkl"
        self.features_path = Path(__file__).parent / "features.json"
        
        # Load or initialize model
        self._initialize_model()
    
    def _initialize_model(self):
        """Load existing model or create a new one"""
        if self.model_path.exists():
            self._load_model()
        else:
            self._create_model()
    
    def _create_model(self):
        """Create and train a new phishing detection model"""
        logger.info("Creating new phishing detection model...")
        
        # Create synthetic training data with realistic phishing indicators
        X_train, y_train = self._create_training_data()
        
        # Initialize and train model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        self.model.fit(X_train_scaled, y_train)
        self.feature_names = [
            'has_ssl', 'subdomain_count', 'has_hyphen', 'domain_length',
            'is_ip', 'has_numbers', 'path_length', 'has_query',
            'special_chars_in_path', 'has_redirects', 'redirect_count'
        ]
        
        # Save model
        self._save_model()
        logger.info("Model created and trained successfully")
    
    def _create_training_data(self):
        """Create synthetic phishing/legitimate training data"""
        # Legitimate website patterns
        legitimate_samples = [
            # Google
            [1, 0, 0, 10, 0, 1, 1, 0, 0, 0, 0],
            # Github
            [1, 0, 0, 10, 0, 0, 5, 1, 0, 0, 0],
            # Amazon
            [1, 0, 0, 6, 0, 0, 3, 1, 0, 0, 0],
            # Microsoft
            [1, 1, 0, 11, 0, 0, 2, 0, 0, 0, 0],
            # Facebook
            [1, 0, 0, 8, 0, 0, 4, 1, 0, 0, 0],
            # Apple
            [1, 0, 0, 5, 0, 0, 2, 0, 0, 0, 0],
            # Cloudflare
            [1, 0, 0, 10, 0, 0, 1, 0, 0, 0, 0],
            # Reddit
            [1, 0, 0, 6, 0, 0, 3, 1, 0, 0, 0],
            # Wikipedia
            [1, 0, 0, 9, 0, 0, 2, 1, 0, 0, 0],
            # Twitter
            [1, 0, 0, 7, 0, 0, 2, 0, 0, 0, 0],
        ] * 50  # Duplicate for more training data
        
        # Phishing website patterns
        phishing_samples = [
            # IP-based phishing
            [0, 0, 0, 15, 1, 1, 25, 1, 3, 1, 2],
            # Long domain with hyphens
            [0, 2, 1, 45, 0, 1, 30, 1, 2, 1, 3],
            # Multiple subdomains
            [0, 4, 0, 35, 0, 0, 20, 1, 1, 1, 2],
            # Suspicious redirects
            [0, 1, 1, 30, 0, 1, 15, 1, 2, 1, 4],
            # Special chars in path
            [0, 1, 0, 25, 0, 1, 40, 1, 5, 1, 2],
            # No SSL + long path
            [0, 2, 1, 40, 0, 0, 50, 1, 3, 1, 1],
            # IP + hyphens
            [0, 1, 1, 20, 1, 0, 35, 1, 2, 1, 2],
            # Mixed suspicious
            [0, 3, 1, 33, 0, 1, 28, 1, 3, 1, 3],
            # Lots of query params
            [0, 2, 0, 30, 0, 1, 60, 1, 1, 1, 2],
            # Redirect chains
            [0, 0, 0, 22, 0, 0, 18, 1, 0, 1, 5],
        ] * 50
        
        X = np.array(legitimate_samples + phishing_samples)
        y = np.array([0] * len(legitimate_samples) + [1] * len(phishing_samples))
        
        return X, y
    
    def predict(self, url: str, features: dict) -> tuple:
        """
        Predict if URL is phishing
        
        Returns:
            (is_phishing, confidence, risk_score)
        """
        # Create feature vector
        feature_vector = self._create_feature_vector(features)
        
        if feature_vector is None:
            return False, 0.5, 0.5
        
        # Scale features
        feature_vector_scaled = self.scaler.transform([feature_vector])
        
        # Get prediction
        prediction = self.model.predict(feature_vector_scaled)[0]
        confidence = max(self.model.predict_proba(feature_vector_scaled)[0])
        
        # Calculate risk score (0-1)
        risk_score = self._calculate_risk_score(features)
        
        is_phishing = prediction == 1
        
        return is_phishing, confidence, risk_score
    
    def _create_feature_vector(self, features: dict) -> np.ndarray:
        """Convert feature dict to feature vector"""
        try:
            # Map features in the correct order
            feature_vector = [
                1 if features.get('has_ssl') else 0,
                features.get('subdomain_count', 0),
                1 if features.get('has_hyphen') else 0,
                features.get('domain_length', 0),
                1 if features.get('is_ip') else 0,
                1 if features.get('has_numbers') else 0,
                features.get('path_length', 0),
                1 if features.get('has_query') else 0,
                features.get('special_chars_in_path', 0),
                1 if features.get('has_redirects') else 0,
                features.get('redirect_count', 0),
            ]
            return np.array(feature_vector, dtype=float)
        except Exception as e:
            logger.error(f"Error creating feature vector: {e}")
            return None
    
    def _calculate_risk_score(self, features: dict) -> float:
        """Calculate overall risk score (0-1)"""
        score = 0.0
        max_score = 10.0
        
        # Assign points for risk factors
        if features.get('is_ip'):
            score += 2.5
        if features.get('has_hyphen'):
            score += 1.0
        if not features.get('has_ssl'):
            score += 2.0
        if features.get('subdomain_count', 0) > 3:
            score += 1.5
        if features.get('redirect_count', 0) > 2:
            score += 2.0
        if features.get('domain_length', 0) > 40:
            score += 1.0
        if features.get('special_chars_in_path', 0) > 3:
            score += 1.5
        
        # Normalize to 0-1
        return min(score / max_score, 1.0)
    
    def _save_model(self):
        """Save model to disk"""
        try:
            joblib.dump(self.model, str(self.model_path))
            joblib.dump(self.scaler, str(self.scaler_path))
            with open(self.features_path, 'w') as f:
                json.dump(self.feature_names, f)
            logger.info(f"Model saved to {self.model_path}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def _load_model(self):
        """Load model from disk"""
        try:
            self.model = joblib.load(str(self.model_path))
            self.scaler = joblib.load(str(self.scaler_path))
            with open(self.features_path, 'r') as f:
                self.feature_names = json.load(f)
            logger.info(f"Model loaded from {self.model_path}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self._create_model()
