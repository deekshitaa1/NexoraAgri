from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from ml.simulator.generate import simulate
from ml.features.engineering import build_features


OUTPUT_DIR = Path("ml/datasets/generated")
OUTPUT_FILE = OUTPUT_DIR / "irrigation_training.csv"

FIELD_ID = "simulation-field-001"

FEATURE_COLUMNS = [
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
]


def generate_dataset(
    start: datetime,
    hours: int,
    seed: int = 42,
) -> pd.DataFrame:

    steps = simulate(
        start=start,
        hours=hours,
        seed=seed,
    )

    rows = []

    for step in steps:

        observation = step.observation
        state = step.state

        rows.append(
            {
                "field_id": FIELD_ID,
                "observed_at": observation.observed_at,
                "soil_moisture": observation.soil_moisture,
                "soil_temperature": observation.soil_temperature,
                "air_temperature": observation.air_temperature,
                "humidity": observation.humidity,
                "rainfall_mm": observation.rainfall_mm,
                "crop": state.crop,
                "soil_type": state.soil_type,
                "crop_stage": state.crop_stage,
                "irrigation_demand_mm": (
                    state.irrigation_demand_mm
                ),
            }
        )

    raw = pd.DataFrame(rows)

    features = build_features(raw)

    features["irrigation_class"] = (
        features["irrigation_demand_mm"]
        .apply(
            lambda value:
                "NONE"
                if value == 0
                else "LOW"
                if value <= 3
                else "MEDIUM"
                if value <= 7
                else "HIGH"
        )
    )

    features = features.dropna(
        subset=FEATURE_COLUMNS
    ).reset_index(drop=True)

    return features


def main() -> None:

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    start = datetime(
        2025,
        1,
        1,
        tzinfo=timezone.utc,
    )

    df = generate_dataset(
        start=start,
        hours=24 * 365,
        seed=42,
    )

    output_columns = [
        "field_id",
        "observed_at",
        *FEATURE_COLUMNS,
        "crop",
        "soil_type",
        "crop_stage",
        "irrigation_demand_mm",
        "irrigation_class",
    ]

    df[output_columns].to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("DATASET GENERATED")
    print("=================")
    print("Rows:", len(df))
    print("Columns:", len(output_columns))
    print("File:", OUTPUT_FILE)
    print()
    print("CLASS DISTRIBUTION")
    print("==================")
    print(
        df["irrigation_class"]
        .value_counts()
        .sort_index()
    )
    print()
    print("TARGET RANGE")
    print("============")
    print(
        "Min:",
        df["irrigation_demand_mm"].min(),
    )
    print(
        "Max:",
        df["irrigation_demand_mm"].max(),
    )


if __name__ == "__main__":
    main()
