from pathlib import Path

import pandas as pd


DATASET = Path(
    "ml/datasets/generated/irrigation_training.csv"
)

df = pd.read_csv(
    DATASET,
    parse_dates=["observed_at"],
)

df = df.sort_values(
    ["field_id", "observed_at"]
).reset_index(drop=True)

print("TEMPORAL AUDIT")
print("==============")
print("Rows:", len(df))
print(
    "Start:",
    df["observed_at"].min(),
)
print(
    "End:",
    df["observed_at"].max(),
)
print()

print("TIME DIFFERENCES")
print("================")

time_diff = (
    df.groupby("field_id")["observed_at"]
    .diff()
    .dropna()
)

print(
    "Minimum interval:",
    time_diff.min(),
)

print(
    "Maximum interval:",
    time_diff.max(),
)

print(
    "Unique intervals:",
    time_diff.unique()[:10],
)

print()

print("ORDER CHECK")
print("===========")

is_sorted = (
    df.groupby("field_id")["observed_at"]
    .apply(lambda x: x.is_monotonic_increasing)
)

print(
    "All fields chronological:",
    bool(is_sorted.all()),
)

print()

print("ROLLING FEATURE CHECK")
print("=====================")

rolling_features = [
    "rainfall_24h",
    "rainfall_72h",
    "moisture_24h_mean",
    "temperature_24h_mean",
]

for feature in rolling_features:
    print(
        f"{feature}:",
        "present" if feature in df.columns
        else "MISSING",
    )

print()

print("RESULT")
print("======")

if (
    is_sorted.all()
    and time_diff.min() == pd.Timedelta(hours=1)
):
    print(
        "PASS - observations are chronological "
        "with hourly intervals"
    )
else:
    print(
        "WARNING - inspect temporal structure"
    )
