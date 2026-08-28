from pathlib import Path

import joblib
import pandas as pd


ROOT = Path(r"D:\NexoraAgri")

MODEL_PATH = ROOT / "ml" / "models" / "irrigation_baseline.joblib"

pipeline = joblib.load(MODEL_PATH)

preprocessor = pipeline.named_steps["preprocessor"]
model = pipeline.named_steps["model"]

feature_names = preprocessor.get_feature_names_out()

importances = model.feature_importances_

importance_df = pd.DataFrame(
    {
        "feature": feature_names,
        "importance": importances,
    }
).sort_values(
    "importance",
    ascending=False,
)

print("NEXORA AGRI FEATURE IMPORTANCE")
print("==============================")
print()
print("Total model features:", len(importance_df))
print()
print("TOP 20 FEATURES")
print("================")
print(
    importance_df.head(20).to_string(index=False)
)

output_path = (
    ROOT
    / "ml"
    / "models"
    / "irrigation_feature_importance.csv"
)

importance_df.to_csv(
    output_path,
    index=False,
)

print()
print("SAVED:")
print(output_path)
