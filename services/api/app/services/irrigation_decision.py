
from __future__ import annotations


def build_irrigation_decision(
    *,
    predicted_class: str,
    confidence: float,
    recommended_irrigation_mm: float,
    soil_moisture: float,
    rainfall_mm: float,
    rainfall_24h: float,
    rainfall_72h: float,
    moisture_deficit: float,
    heat_stress: float,
    crop_stage: float,
) -> dict:

    predicted_class = predicted_class.upper()

    confidence = round(
        max(0.0, min(1.0, confidence)),
        4,
    )

    recommended_irrigation_mm = round(
        max(
            0.0,
            min(12.0, recommended_irrigation_mm),
        ),
        2,
    )

    reasons: list[str] = []

    # Recent rainfall can make immediate irrigation unnecessary.
    if rainfall_mm >= 8.0:
        return {
            "action": "No irrigation recommended because significant rainfall was recently observed.",
            "urgency": "NONE",
            "predicted_class": predicted_class,
            "confidence": confidence,
            "recommended_irrigation_mm": 0.0,
            "reasons": [
                "Recent rainfall reduces immediate irrigation requirement.",
                f"Observed rainfall: {rainfall_mm:.2f} mm.",
            ],
        }

    if rainfall_24h >= 12.0:
        reasons.append(
            "Recent 24-hour rainfall is reducing water stress."
        )

    if rainfall_72h >= 20.0:
        reasons.append(
            "Recent 72-hour rainfall indicates meaningful accumulated precipitation."
        )

    if soil_moisture < 28.0:
        reasons.append(
            "Soil moisture is below the preferred moisture threshold."
        )
    elif soil_moisture < 32.0:
        reasons.append(
            "Soil moisture shows some irrigation requirement."
        )
    else:
        reasons.append(
            "Soil moisture is currently relatively adequate."
        )

    if moisture_deficit > 5.0:
        reasons.append(
            "The soil has a significant moisture deficit."
        )
    elif moisture_deficit > 0.0:
        reasons.append(
            "A measurable soil moisture deficit is present."
        )

    if heat_stress > 2.0:
        reasons.append(
            "Elevated heat stress may increase crop water demand."
        )

    if crop_stage > 0.1 and crop_stage < 0.95:
        reasons.append(
            "The crop is in an active growth stage."
        )

    # Decision policy combines the ML class with predicted quantity.
    if predicted_class == "NONE":
        urgency = "NONE"

        # Never recommend meaningful irrigation when the classifier
        # determines that irrigation is unnecessary.
        recommended_irrigation_mm = 0.0

        action = (
            "No irrigation required. Continue monitoring soil moisture."
        )

    elif predicted_class == "LOW":
        if recommended_irrigation_mm >= 3.0:
            urgency = "LOW"
            action = (
                f"Consider light irrigation of approximately "
                f"{recommended_irrigation_mm:.2f} mm."
            )
        else:
            urgency = "LOW"
            action = (
                f"Monitor soil moisture and consider light irrigation "
                f"of approximately {recommended_irrigation_mm:.2f} mm."
            )

    elif predicted_class == "MEDIUM":
        urgency = "MEDIUM"
        action = (
            f"Recommend irrigation of approximately "
            f"{recommended_irrigation_mm:.2f} mm."
        )

    elif predicted_class == "HIGH":
        urgency = "HIGH"
        action = (
            f"Irrigation is recommended promptly at approximately "
            f"{recommended_irrigation_mm:.2f} mm."
        )

    else:
        urgency = "UNKNOWN"
        action = (
            "Unable to determine irrigation urgency."
        )
        recommended_irrigation_mm = 0.0

        reasons.append(
            "The prediction class is not recognized by the decision policy."
        )

    return {
        "action": action,
        "urgency": urgency,
        "predicted_class": predicted_class,
        "confidence": confidence,
        "recommended_irrigation_mm": recommended_irrigation_mm,
        "reasons": reasons,
    }
