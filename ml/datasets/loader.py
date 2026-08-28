from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
API_ROOT = PROJECT_ROOT / "services" / "api"

sys.path.insert(0, str(API_ROOT))


from app.db.session import SessionLocal
from app.models.field_observation import FieldObservation


def load_field_observations() -> pd.DataFrame:
    with SessionLocal() as db:
        rows = db.query(FieldObservation).order_by(
            FieldObservation.observed_at
        ).all()

        data = [
            {
                "id": str(row.id),
                "field_id": str(row.field_id),
                "observed_at": row.observed_at,
                "soil_moisture": row.soil_moisture,
                "soil_temperature": row.soil_temperature,
                "air_temperature": row.air_temperature,
                "humidity": row.humidity,
                "rainfall_mm": row.rainfall_mm,
                "source": row.source,
            }
            for row in rows
        ]

    dataframe = pd.DataFrame(data)

    if not dataframe.empty:
        dataframe["observed_at"] = pd.to_datetime(
            dataframe["observed_at"],
            utc=True,
        )

    return dataframe


if __name__ == "__main__":
    df = load_field_observations()

    print(f"ROWS: {len(df)}")
    print(f"COLUMNS: {list(df.columns)}")
    print()
    print(df.head())
