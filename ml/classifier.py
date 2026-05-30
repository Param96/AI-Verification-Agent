import joblib
import pandas as pd
from typing import Dict, Any, Tuple
from config import VERIFICATION_MODEL_PATH
from utils.logger import logger

class VerificationClassifier:
    def __init__(self):
        self.model = None
        self.label_mapping = {
            0: "VALID",
            1: "PARTIAL_MATCH",
            2: "OUTDATED",
            3: "INVALID",
            4: "BROKEN_LINK",
            5: "MISSING_DATA"
        }
        self._load_model()

    def _load_model(self):
        if VERIFICATION_MODEL_PATH.exists():
            try:
                self.model = joblib.load(VERIFICATION_MODEL_PATH)
                logger.info("ML Verification Model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load ML model: {e}")
        else:
            logger.warning(f"ML Model not found at {VERIFICATION_MODEL_PATH}. Will fallback to rule-based engine.")

    def predict(self, features: Dict[str, Any]) -> Tuple[str, float]:
        """
        Predicts the status based on feature dictionary.
        Returns (Prediction_Label, Confidence_Score)
        """
        if not self.model:
            return self._rule_based_fallback(features)

        # Convert to DataFrame to match expected input for sklearn/xgboost
        df = pd.DataFrame([features])
        
        try:
            # Reorder columns just in case
            prediction = self.model.predict(df)[0]
            probabilities = self.model.predict_proba(df)[0]
            confidence = float(max(probabilities))
            
            label = self.label_mapping.get(prediction, "INVALID")
            return label, confidence
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return self._rule_based_fallback(features)

    def _rule_based_fallback(self, features: Dict[str, Any]) -> Tuple[str, float]:
        """Simple fallback if model isn't trained yet."""
        if features.get('broken_link') == 1:
            return "BROKEN_LINK", 1.0
            
        sim = features.get('course_name_similarity', 0.0)
        if sim > 0.8:
            return "VALID", float(sim)
        elif sim > 0.4:
            return "PARTIAL_MATCH", float(sim)
        else:
            return "INVALID", 1.0 - float(sim)
