from __future__ import annotations

import pandas as pd


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    data = df.copy()

    data = data.sort_values(
        ["field_id", "observed_at"]
    ).reset_index(drop=True)

    data["hour"] = data["observed_at"].dt.hour
    data["day_of_year"] = data["observed_at"].dt.dayofyear

    previous_time = (
        data.groupby("field_id")["observed_at"]
        .shift(1)
    )

    time_gap_hours = (
        data["observed_at"] - previous_time
    ).dt.total_seconds() / 3600

    valid_continuity = time_gap_hours <= 1.5

    moisture_change = (
        data.groupby("field_id")["soil_moisture"]
        .diff()
    )

    temperature_change = (
        data.groupby("field_id")["air_temperature"]
        .diff()
    )

    data["moisture_change"] = moisture_change.where(
        valid_continuity
    )

    data["temperature_change"] = temperature_change.where(
        valid_continuity
    )

    data["rainfall_24h"] = (
        data.groupby("field_id")["rainfall_mm"]
        .transform(
            lambda series: series.rolling(
                window=24,
                min_periods=1,
            ).sum()
        )
    )

    data["rainfall_72h"] = (
        data.groupby("field_id")["rainfall_mm"]
        .transform(
            lambda series: series.rolling(
                window=72,
                min_periods=1,
            ).sum()
        )
    )

    data["moisture_24h_mean"] = (
        data.groupby("field_id")["soil_moisture"]
        .transform(
            lambda series: series.rolling(
                window=24,
                min_periods=1,
            ).mean()
        )
    )

    data["temperature_24h_mean"] = (
        data.groupby("field_id")["air_temperature"]
        .transform(
            lambda series: series.rolling(
                window=24,
                min_periods=1,
            ).mean()
        )
    )

    data["moisture_deficit"] = (
        35.0 - data["soil_moisture"]
    ).clip(lower=0)

    data["heat_stress"] = (
        data["air_temperature"] - 30.0
    ).clip(lower=0)

    data["time_gap_hours"] = time_gap_hours

    return data
