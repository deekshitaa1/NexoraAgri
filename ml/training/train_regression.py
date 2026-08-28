from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


PROJECT_ROOT = Path(r"D:\NexoraAgri")

DATA_DIR = PROJECT_ROOT / "ml" / "datasets" / "generated" / "splits"
MODEL_DIR = PROJECT_ROOT / "ml" / "models"

MODEL_DIR.mkdir(parents=True, exist_ok=True)


TARGET = "irrigation_demand_mm"

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
        raise FileNotFoundError(
            f"Dataset split not found: {path}"
        )

    return pd.read_csv(
        path,
        parse_dates=["observed_at"],
    )


def evaluate(
    model: Pipeline,
    dataframe: pd.DataFrame,
    name: str,
) -> dict[str, float]:

    X = dataframe[FEATURES]
    y = dataframe[TARGET]

    predictions = model.predict(X)

    mae = mean_absolute_error(y, predictions)
    rmse = mean_squared_error(
        y,
        predictions,
    ) ** 0.5
    r2 = r2_score(y, predictions)

    print()
    print(f"{name.upper()} EVALUATION")
    print("=" * 60)
    print(f"Rows:        {len(dataframe)}")
    print(f"MAE:         {mae:.4f} mm")
    print(f"RMSE:        {rmse:.4f} mm")
    print(f"R2:          {r2:.4f}")

    return {
        "mae": round(float(mae), 6),
        "rmse": round(float(rmse), 6),
        "r2": round(float(r2), 6),
    }


def main() -> None:

    print("NEXORA AGRI IRRIGATION REGRESSION")
    print("=================================")

    train = load_split("train")
    validation = load_split("validation")
    test = load_split("test")

    print()
    print("DATA")
    print("====")
    print(f"Train:      {len(train)}")
    print(f"Validation: {len(validation)}")
    print(f"Test:       {len(test)}")

    print()
    print("TARGET")
    print("======")
    print(TARGET)
    print(
        f"Min: {train[TARGET].min():.2f}"
    )
    print(
        f"Max: {train[TARGET].max():.2f}"
    )

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                "passthrough",
                NUMERIC_FEATURES,
            ),
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
                CATEGORICAL_FEATURES,
            ),
        ]
    )

    model = RandomForestRegressor(
        n_estimators=500,
        random_state=42,
        n_jobs=-1,
        min_samples_leaf=2,
    )

    pipeline = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor,
            ),
            (
                "model",
                model,
            ),
        ]
    )

    print()
    print("TRAINING RANDOM FOREST REGRESSOR...")
    print("===================================")

    pipeline.fit(
        train[FEATURES],
        train[TARGET],
    )

    print("TRAINING COMPLETE")

    validation_metrics = evaluate(
        pipeline,
        validation,
        "Validation",
    )

    test_metrics = evaluate(
        pipeline,
        test,
        "Test",
    )

    model_path = (
        MODEL_DIR
        / "irrigation_demand_regressor.joblib"
    )

    metrics_path = (
        MODEL_DIR
        / "irrigation_demand_regressor_metrics.json"
    )

    joblib.dump(
        pipeline,
        model_path,
    )

    metrics = {
        "model": "RandomForestRegressor",
        "target": TARGET,
        "features": FEATURES,
        "train_rows": len(train),
        "validation_rows": len(validation),
        "test_rows": len(test),
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
    print("REGRESSION TRAINING COMPLETE")


if __name__ == "__main__":
    main()
