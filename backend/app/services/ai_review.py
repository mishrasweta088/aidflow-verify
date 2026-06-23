from app.models.aid_request import AidRequest


def generate_ai_review(aid_request: AidRequest) -> dict[str, str]:
    text = f"{aid_request.title} {aid_request.description} {aid_request.category}".lower()

    urgency = "medium"

    high_urgency_keywords = [
        "urgent",
        "emergency",
        "medicine",
        "medical",
        "hospital",
        "baby",
        "child",
        "no food",
        "homeless",
        "shelter",
    ]

    if any(keyword in text for keyword in high_urgency_keywords):
        urgency = "high"

    missing_fields = []

    if not aid_request.address:
        missing_fields.append("address")

    if aid_request.latitude is None or aid_request.longitude is None:
        missing_fields.append("location coordinates")

    risk_indicators = []

    if len(aid_request.description.strip()) < 25:
        risk_indicators.append("description is too short")

    if not risk_indicators:
        risk_indicators.append("no obvious risk indicators found")

    checklist = [
        "Confirm requester identity",
        "Confirm aid category and exact need",
        "Confirm location",
        "Check if request is still active",
        "Collect verification notes or proof",
    ]

    return {
        "ai_summary": f"{aid_request.title}: {aid_request.description}",
        "ai_urgency": urgency,
        "ai_missing_fields": ", ".join(missing_fields) if missing_fields else "none",
        "ai_risk_indicators": ", ".join(risk_indicators),
        "ai_verification_checklist": "; ".join(checklist),
    }