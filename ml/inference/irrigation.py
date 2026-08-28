from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = PROJECT_ROOT / "ml" / "models"

CLASSIFIER_PATH = MODEL_DIR / "irrigation_baseline.joblib"
REGRESSOR_PATH = MODEL_DIR / "irrigation_demand_regressor.joblib"


_classifier = None
_regressor = None


def get_irrigation_model():
    global _classifier

    if _classifier is None:
        if not CLASSIFIER_PATH.exists():
            raise FileNotFoundError(
                f"Irrigation classifier not found: {CLASSIFIER_PATH}"
            )

        _classifier = joblib.load(CLASSIFIER_PATH)

    return _classifier


def get_irrigation_regressor():
    global _regressor

    if _regressor is None:
        if not REGRESSOR_PATH.exists():
            raise FileNotFoundError(
                f"Irrigation regressor not found: {REGRESSOR_PATH}"
            )

        _regressor = joblib.load(REGRESSOR_PATH)

    return _regressor


def predict_irrigation(
    features: dict[str, Any],
) -> dict[str, Any]:

    classifier = get_irrigation_model()
    regressor = get_irrigation_regressor()

    # The sklearn pipelines were trained with a DataFrame
    # containing named feature columns.
    feature_frame = pd.DataFrame([features])

    predicted_class = classifier.predict(
        feature_frame
    )[0]

    classes = list(classifier.classes_)

    probabilities_array = classifier.predict_proba(
        feature_frame
    )[0]

    probabilities = {
        str(label): round(float(probability), 6)
        for label, probability in zip(
            classes,
            probabilities_array,
        )
    }

    confidence = probabilities[str(predicted_class)]

    regression_prediction = regressor.predict(
        feature_frame
    )[0]

    recommended_irrigation_mm = round(
        max(
            0.0,
            min(
                12.0,
                float(regression_prediction),
            ),
        ),
        2,
    )

    return {
        "predicted_class": str(predicted_class),
        "confidence": round(float(confidence), 6),
        "probabilities": probabilities,
        "recommended_irrigation_mm": recommended_irrigation_mm,
    }
