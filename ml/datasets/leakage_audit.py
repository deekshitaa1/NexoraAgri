from pathlib import Path

import pandas as pd


DATASET = Path(
    "ml/datasets/generated/irrigation_training.csv"
)

TARGETS = {
    "irrigation_demand_mm",
    "irrigation_class",
}

df = pd.read_csv(DATASET)

print("LEAKAGE AUDIT")
print("=============")
print("Rows:", len(df))
print("Columns:", len(df.columns))
print()

print("TARGET COLUMNS:")
for target in TARGETS:
    print(" ", target)

print()
print("FEATURE COLUMNS:")
feature_columns = [
    column
    for column in df.columns
    if column not in TARGETS
]

for column in feature_columns:
    print(" ", column)

print()
print("POTENTIAL LEAKAGE:")
suspects = [
    column
    for column in feature_columns
    if any(
        keyword in column.lower()
        for keyword in [
            "demand",
            "irrigation",
            "target",
            "label",
        ]
    )
]

if suspects:
    for column in suspects:
        print("  WARNING:", column)
else:
    print("  NONE")

print()
print("MISSING VALUES:")
print(df.isna().sum().sum())

print()
print("DUPLICATE ROWS:")
print(df.duplicated().sum())

print()
print("RESULT:")
if suspects:
    print("FAIL - potential target leakage detected")
else:
    print("PASS - no obvious target leakage detected")
