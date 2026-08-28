from ml.datasets.loader import load_field_observations
from ml.features.engineering import build_features


df = load_field_observations()

features = build_features(df)

print("FEATURE ENGINEERING REPORT")
print("==========================")
print(f"Input rows: {len(df)}")
print(f"Output rows: {len(features)}")
print()
print("New features:")

new_features = [
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

for feature in new_features:
    print(f"  {feature}")

print()
print(
    features[
        [
            "observed_at",
            "soil_moisture",
            "rainfall_mm",
            "rainfall_24h",
            "rainfall_72h",
            "moisture_change",
            "moisture_deficit",
            "heat_stress",
        ]
    ].tail(10).to_string(index=False)
)
