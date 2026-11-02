
"""Train and evaluate the baseline fraud-detection model."""

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "fraud_sample.csv"
MODEL_DIR = PROJECT_ROOT / "backend" / "models"
MODEL_PATH = MODEL_DIR / "fraud_model.joblib"
METRICS_PATH = MODEL_DIR / "evaluation.json"

TARGET = "isFraud"
NUMERIC_FEATURES = [
    "step",
    "amount",
    "oldbalanceOrg",
    "newbalanceOrig",
    "oldbalanceDest",
    "newbalanceDest",
]
CATEGORICAL_FEATURES = ["type"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Training data not found: {DATA_PATH}"
        )

    print("Loading sampled transaction data...")
    data = pd.read_csv(DATA_PATH)

    required_columns = FEATURES + [TARGET]
    missing_columns = set(required_columns) - set(data.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    # Convert the target to integer labels and validate the data.
    data[TARGET] = pd.to_numeric(data[TARGET], errors="raise").astype(int)

    if not data[TARGET].isin([0, 1]).all():
        raise ValueError("The fraud target must contain only 0 and 1.")

    if data[required_columns].isnull().any().any():
        raise ValueError("Missing values found in training data.")

    X = data[FEATURES]
    y = data[TARGET]

    print(f"Transactions: {len(data):,}")
    print(f"Fraud cases: {int(y.sum()):,}")
    print(f"Fraud rate: {y.mean() * 100:.4f}%")

    # Preserve the fraud proportion in both subsets.
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    preprocessing = ColumnTransformer(
        transformers=[
            (
                "numeric",
                StandardScaler(),
                NUMERIC_FEATURES,
            ),
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                CATEGORICAL_FEATURES,
            ),
        ]
    )

    model = Pipeline(
        steps=[
            ("preprocessing", preprocessing),
            (
                "classifier",
                LogisticRegression(
                    class_weight="balanced",
                    solver="liblinear",
                    max_iter=200,
                    random_state=42,
                ),
            ),
        ]
    )

    print("\nTraining baseline Logistic Regression...")
    model.fit(X_train, y_train)

    print("Evaluating on the held-out test set...")
    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]

    metrics = {
        "model": "LogisticRegression",
        "threshold": 0.5,
        "training_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "training_fraud_cases": int(y_train.sum()),
        "test_fraud_cases": int(y_test.sum()),
        "precision": float(
            precision_score(y_test, predictions, zero_division=0)
        ),
        "recall": float(
            recall_score(y_test, predictions, zero_division=0)
        ),
        "f1_score": float(
            f1_score(y_test, predictions, zero_division=0)
        ),
        "average_precision": float(
            average_precision_score(y_test, probabilities)
        ),
        "confusion_matrix": confusion_matrix(
            y_test, predictions, labels=[0, 1]
        ).tolist(),
    }

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    with METRICS_PATH.open("w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=2)

    print("\n--- BASELINE RESULTS ---")
    print(f"Precision:         {metrics['precision']:.4f}")
    print(f"Recall:            {metrics['recall']:.4f}")
    print(f"F1-score:          {metrics['f1_score']:.4f}")
    print(f"Average precision: {metrics['average_precision']:.4f}")
    print("\nConfusion matrix (rows = actual, columns = predicted):")
    print("                 Predicted legitimate | Predicted fraud")
    print(f"Actual legitimate: {metrics['confusion_matrix'][0]}")
    print(f"Actual fraud:      {metrics['confusion_matrix'][1]}")
    print("\nClassification report:")
    print(
        classification_report(
            y_test,
            predictions,
            labels=[0, 1],
            target_names=["legitimate", "fraud"],
            zero_division=0,
        )
    )

    print(f"Model saved to: {MODEL_PATH}")
    print(f"Metrics saved to: {METRICS_PATH}")


if __name__ == "__main__":
    main()
