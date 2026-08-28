from __future__ import annotations

import pandas as pd


REQUIRED_COLUMNS = [
    "field_id",
    "observed_at",
    "soil_moisture",
    "soil_temperature",
    "air_temperature",
    "humidity",
    "rainfall_mm",
    "source",
]


def validate_observations(df: pd.DataFrame) -> dict:
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    duplicate_count = int(
        df.duplicated(
            subset=["field_id", "observed_at"]
        ).sum()
    )

    invalid_moisture = int(
        ((df["soil_moisture"] < 0) | (df["soil_moisture"] > 100))
        .fillna(False)
        .sum()
    )

    invalid_humidity = int(
        ((df["humidity"] < 0) | (df["humidity"] > 100))
        .fillna(False)
        .sum()
    )

    invalid_rainfall = int(
        (df["rainfall_mm"] < 0)
        .fillna(False)
        .sum()
    )

    return {
        "rows": len(df),
        "duplicate_field_timestamps": duplicate_count,
        "invalid_soil_moisture": invalid_moisture,
        "invalid_humidity": invalid_humidity,
        "invalid_rainfall": invalid_rainfall,
        "missing_values": {
            column: int(df[column].isna().sum())
            for column in REQUIRED_COLUMNS
        },
    }
