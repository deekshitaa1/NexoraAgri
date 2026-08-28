from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT / "ml" / "datasets" / "generated" / "splits"
MODEL_DIR = ROOT / "ml" / "models"

MODEL_DIR.mkdir(parents=True, exist_ok=True)


TARGET = "irrigation_class"

FEATURES = [
    "soil_moisture",
    "soil_temperature",
    "air_temperature",
    "humidity",
    "rainfall_mm",
    "hour",
    "day_of_year",
    "moisture_change",
    "temperature_change",
    "rainfall_24h",
    "rainfall_72h",
    "moisture_24h_mean",
    "temperature_24h_mean",
    "moisture_deficit",
    "heat_stress",
    "crop",
    "soil_type",
    "crop_stage",
]


NUMERIC_FEATURES = [
    "soil_moisture",
    "soil_temperature",
    "air_temperature",
    "humidity",
    "rainfall_mm",
    "hour",
    "day_of_year",
    "moisture_change",
    "temperature_change",
    "rainfall_24h",
    "rainfall_72h",
    "moisture_24h_mean",
    "temperature_24h_mean",
    "moisture_deficit",
    "heat_stress",
    "crop_stage",
]


CATEGORICAL_FEATURES = [
    "crop",
    "soil_type",
]


def load_split(name: str) -> pd.DataFrame:
    path = DATA_DIR / f"{name}.csv"

    if not path.exists():
        raise FileNotFoundError(f"Missing dataset split: {path}")

    return pd.read_csv(path)


def build_pipeline() -> Pipeline:
    numeric_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="median"),
            ),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="most_frequent"),
            ),
            (
                "onehot",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False,
                ),
            ),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                numeric_pipeline,
                NUMERIC_FEATURES,
            ),
            (
                "categorical",
                categorical_pipeline,
                CATEGORICAL_FEATURES,
            ),
        ],
        remainder="drop",
    )

    model = RandomForestClassifier(
        n_estimators=400,
        max_depth=14,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )


def evaluate(
    pipeline: Pipeline,
    X: pd.DataFrame,
    y: pd.Series,
    split_name: str,
) -> dict:
    predictions = pipeline.predict(X)

    accuracy = accuracy_score(y, predictions)

    macro_f1 = f1_score(
        y,
        predictions,
        average="macro",
        zero_division=0,
    )

    weighted_f1 = f1_score(
        y,
        predictions,
        average="weighted",
        zero_division=0,
    )

    labels = ["NONE", "LOW", "MEDIUM", "HIGH"]

    report = classification_report(
        y,
        predictions,
        labels=labels,
        output_dict=True,
        zero_division=0,
    )

    matrix = confusion_matrix(
        y,
        predictions,
        labels=labels,
    )

    print()
    print(f"{split_name.upper()} EVALUATION")
    print("=" * 60)
    print(f"Rows:        {len(y)}")
    print(f"Accuracy:    {accuracy:.4f}")
    print(f"Macro F1:    {macro_f1:.4f}")
    print(f"Weighted F1: {weighted_f1:.4f}")

    print()
    print("CLASSIFICATION REPORT")
    print("=====================")

    print(
        classification_report(
            y,
            predictions,
            labels=labels,
            zero_division=0,
        )
    )

    print("CONFUSION MATRIX")
    print("================")
    print("Labels:", labels)

    for label, row in zip(labels, matrix):
        print(f"{label:7} {row.tolist()}")

    return {
        "rows": len(y),
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "classification_report": report,
        "confusion_matrix": matrix.tolist(),
    }


def main() -> None:
    print("NEXORA AGRI BASELINE TRAINING")
    print("==============================")

    train = load_split("train")
    validation = load_split("validation")
    test = load_split("test")

    missing_features = [
        feature
        for feature in FEATURES
        if feature not in train.columns
    ]

    if missing_features:
        raise ValueError(
            f"Missing features: {missing_features}"
        )

    if TARGET not in train.columns:
        raise ValueError(
            f"Missing target column: {TARGET}"
        )

    X_train = train[FEATURES]
    y_train = train[TARGET]

    X_validation = validation[FEATURES]
    y_validation = validation[TARGET]

    X_test = test[FEATURES]
    y_test = test[TARGET]

    print()
    print("DATA")
    print("====")
    print(f"Train:      {len(train)}")
    print(f"Validation: {len(validation)}")
    print(f"Test:       {len(test)}")

    print()
    print("FEATURES")
    print("========")
    print(f"Total:      {len(FEATURES)}")
    print(f"Numeric:    {len(NUMERIC_FEATURES)}")
    print(f"Categorical:{len(CATEGORICAL_FEATURES)}")

    print()
    print("TARGET")
    print("======")
    print(y_train.value_counts().sort_index())

    pipeline = build_pipeline()

    print()
    print("TRAINING RANDOM FOREST...")
    print("=========================")

    pipeline.fit(
        X_train,
        y_train,
    )

    print("TRAINING COMPLETE")

    validation_metrics = evaluate(
        pipeline,
        X_validation,
        y_validation,
        "validation",
    )

    test_metrics = evaluate(
        pipeline,
        X_test,
        y_test,
        "test",
    )

    model_path = MODEL_DIR / "irrigation_baseline.joblib"

    joblib.dump(
        pipeline,
        model_path,
    )

    metrics_path = MODEL_DIR / "irrigation_baseline_metrics.json"

    metrics = {
        "model": "RandomForestClassifier",
        "random_state": 42,
        "features": FEATURES,
        "target": TARGET,
        "validation": validation_metrics,
        "test": test_metrics,
    }

    metrics_path.write_text(
        json.dumps(
            metrics,
            indent=2,
        )
    )

    print()
    print("ARTIFACTS")
    print("=========")
    print(f"Model:   {model_path}")
    print(f"Metrics: {metrics_path}")

    print()
    print("BASELINE TRAINING COMPLETE")


if __name__ == "__main__":
    main()
