from pathlib import Path

import pandas as pd


INPUT = Path(
    "ml/datasets/generated/irrigation_training.csv"
)

OUTPUT_DIR = Path(
    "ml/datasets/generated/splits"
)

TRAIN_FILE = OUTPUT_DIR / "train.csv"
VALIDATION_FILE = OUTPUT_DIR / "validation.csv"
TEST_FILE = OUTPUT_DIR / "test.csv"


def main() -> None:

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    df = pd.read_csv(
        INPUT,
        parse_dates=["observed_at"],
    )

    df = df.sort_values(
        "observed_at"
    ).reset_index(drop=True)

    total = len(df)

    train_end = int(total * 0.70)
    validation_end = int(total * 0.85)

    train = df.iloc[:train_end].copy()
    validation = df.iloc[
        train_end:validation_end
    ].copy()
    test = df.iloc[
        validation_end:
    ].copy()

    train.to_csv(
        TRAIN_FILE,
        index=False,
    )

    validation.to_csv(
        VALIDATION_FILE,
        index=False,
    )

    test.to_csv(
        TEST_FILE,
        index=False,
    )

    print("TEMPORAL DATASET SPLIT")
    print("======================")
    print()

    print(
        f"Total rows:      {len(df)}"
    )
    print(
        f"Train rows:      {len(train)}"
    )
    print(
        f"Validation rows: {len(validation)}"
    )
    print(
        f"Test rows:       {len(test)}"
    )

    print()

    print("DATE RANGES")
    print("===========")

    print(
        "Train:",
        train["observed_at"].min(),
        "?",
        train["observed_at"].max(),
    )

    print(
        "Validation:",
        validation["observed_at"].min(),
        "?",
        validation["observed_at"].max(),
    )

    print(
        "Test:",
        test["observed_at"].min(),
        "?",
        test["observed_at"].max(),
    )

    print()

    print("CLASS DISTRIBUTION")
    print("==================")

    for name, subset in [
        ("TRAIN", train),
        ("VALIDATION", validation),
        ("TEST", test),
    ]:

        print()
        print(name)

        print(
            subset[
                "irrigation_class"
            ].value_counts(
                normalize=False
            ).sort_index()
        )

    print()

    print("FILES")
    print("=====")
    print(TRAIN_FILE)
    print(VALIDATION_FILE)
    print(TEST_FILE)


if __name__ == "__main__":
    main()
