import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
from sklearn.model_selection import train_test_split
from config import VERIFICATION_MODEL_PATH
from ml.evaluator import evaluate_model
from utils.logger import logger


def generate_synthetic_data(num_samples: int = 1000):
    """Generates synthetic feature data representing our ML features for training."""
    logger.info(f"Generating {num_samples} synthetic training samples...")
    np.random.seed(42)

    # Feature columns based on feature_engineering.py
    data = {
        "broken_link": np.random.choice([0, 1], size=num_samples, p=[0.9, 0.1]),
        "redirect_detected": np.random.choice([0, 1], size=num_samples, p=[0.8, 0.2]),
        "page_length": np.random.normal(5000, 2000, num_samples).astype(int),
        "response_time": np.random.exponential(500, num_samples),
        "course_name_similarity": np.random.beta(5, 2, num_samples),
        "institute_similarity": np.random.beta(7, 1, num_samples),
        "description_similarity": np.random.beta(4, 3, num_samples),
        "fees_difference": np.random.exponential(1000, num_samples),
        "duration_difference": np.random.exponential(2, num_samples),
        "predicted_domain_conf": np.random.uniform(0.5, 1.0, num_samples),
        "domain_match": np.random.choice([0, 1], size=num_samples, p=[0.2, 0.8]),
        "course_type_similarity": np.random.beta(8, 2, num_samples),
        "scholarship_detected": np.random.choice([0, 1], size=num_samples),
        "certificate_exists": np.random.choice([0, 1], size=num_samples),
    }

    df = pd.DataFrame(data)

    # Heuristics to assign labels based on synthetic features
    # Labels: 0: "VALID", 1: "PARTIAL_MATCH", 2: "OUTDATED", 3: "INVALID", 4: "BROKEN_LINK", 5: "MISSING_DATA"
    labels = []
    for _, row in df.iterrows():
        if row["broken_link"] == 1:
            labels.append(4)  # BROKEN_LINK
        elif row["course_name_similarity"] < 0.3:
            labels.append(3)  # INVALID
        elif row["fees_difference"] > 500 or row["duration_difference"] > 6:
            labels.append(2)  # OUTDATED
        elif row["course_name_similarity"] > 0.8 and row["domain_match"] == 1:
            labels.append(0)  # VALID
        else:
            labels.append(1)  # PARTIAL_MATCH

    return df, pd.Series(labels)


def train_model():
    """Trains the XGBoost classifier on the synthetic dataset."""
    X, y = generate_synthetic_data(2000)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    logger.info("Training XGBoost Classifier...")

    # We use XGBClassifier for multi-class prediction
    clf = xgb.XGBClassifier(
        objective="multi:softprob",
        num_class=6,
        max_depth=4,
        learning_rate=0.1,
        n_estimators=100,
        random_state=42,
    )

    clf.fit(X_train, y_train)

    logger.info("Training complete. Evaluating on test set...")
    y_pred = clf.predict(X_test)

    labels_mapping = {
        0: "VALID",
        1: "PARTIAL_MATCH",
        2: "OUTDATED",
        3: "INVALID",
        4: "BROKEN_LINK",
        5: "MISSING_DATA",
    }

    evaluate_model(y_test, y_pred, labels_mapping)

    # Save the model
    joblib.dump(clf, VERIFICATION_MODEL_PATH)
    logger.info(f"Model saved to {VERIFICATION_MODEL_PATH}")


if __name__ == "__main__":
    train_model()
