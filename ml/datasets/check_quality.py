from ml.datasets.loader import load_field_observations
from ml.datasets.quality import validate_observations


df = load_field_observations()

report = validate_observations(df)

print("DATA QUALITY REPORT")
print("===================")

for key, value in report.items():
    print(f"{key}: {value}")
