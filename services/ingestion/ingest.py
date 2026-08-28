from datetime import datetime, timezone
from pathlib import Path
import sys
from uuid import UUID


PROJECT_ROOT = Path(__file__).resolve().parents[2]
API_ROOT = PROJECT_ROOT / "services" / "api"

sys.path.insert(0, str(API_ROOT))
sys.path.insert(0, str(PROJECT_ROOT))


from app.db.session import SessionLocal
from app.services.observation_ingestion import store_observations
from ml.simulator.generate import generate_observations


FIELD_ID = UUID("d5b518d4-310b-4e95-8b68-27f34dc7c057")


def main() -> None:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)

    generated = generate_observations(
        start=start,
        hours=24 * 30,
        seed=42,
    )

    payload = [
        {
            "field_id": FIELD_ID,
            "observed_at": item.observed_at,
            "soil_moisture": item.soil_moisture,
            "soil_temperature": item.soil_temperature,
            "air_temperature": item.air_temperature,
            "humidity": item.humidity,
            "rainfall_mm": item.rainfall_mm,
            "source": item.source,
        }
        for item in generated
    ]

    with SessionLocal() as db:
        count = store_observations(db, payload)

    print(f"INGESTED OBSERVATIONS: {count}")


if __name__ == "__main__":
    main()
