from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd


ROOT = Path(r"D:\NexoraAgri")

MODEL_PATH = (
    ROOT
    / "ml"
    / "models"
    / "irrigation_baseline.joblib"
)

TEST_PATH = (
    ROOT
    / "ml"
    / "datasets"
    / "generated"
    / "splits"
    / "test.csv"
)


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


def main() -> None:
    model = joblib.load(MODEL_PATH)

    test = pd.read_csv(
        TEST_PATH,
        parse_dates=["observed_at"],
    )

    X = test[FEATURES]

    predictions = model.predict(X)
    probabilities = model.predict_proba(X)

    classes = list(model.classes_)

    result = test[
        [
            "observed_at",
            "field_id",
            "soil_moisture",
            "rainfall_mm",
            "irrigation_class",
        ]
    ].copy()

    result["predicted_class"] = predictions
    result["confidence"] = probabilities.max(axis=1)

    for index, class_name in enumerate(classes):
        result[
            f"probability_{class_name.lower()}"
        ] = probabilities[:, index]

    print("NEXORA AGRI PREDICTION ANALYSIS")
    print("===============================")
    print()
    print("Rows:", len(result))
    print("Classes:", classes)

    print()
    print("SAMPLE PREDICTIONS")
    print("==================")

    columns = [
        "observed_at",
        "soil_moisture",
        "rainfall_mm",
        "irrigation_class",
        "predicted_class",
        "confidence",
    ]

    print(
        result[columns]
        .head(15)
        .to_string(index=False)
    )

    print()
    print("CONFIDENCE")
    print("==========")

    print(
        "Mean:",
        round(result["confidence"].mean(), 4),
    )

    print(
        "Minimum:",
        round(result["confidence"].min(), 4),
    )

    print(
        "Maximum:",
        round(result["confidence"].max(), 4),
    )

    high = result[
        result["predicted_class"] == "HIGH"
    ]

    print()
    print("HIGH PREDICTIONS")
    print("================")
    print("Count:", len(high))

    if len(high) > 0:
        print(
            high[
                [
                    "observed_at",
                    "soil_moisture",
                    "irrigation_class",
                    "predicted_class",
                    "confidence",
                ]
            ]
            .head(10)
            .to_string(index=False)
        )

    output_path = (
        ROOT
        / "ml"
        / "models"
        / "test_predictions.csv"
    )

    result.to_csv(
        output_path,
        index=False,
    )

    print()
    print("SAVED:")
    print(output_path)


if __name__ == "__main__":
    main()
