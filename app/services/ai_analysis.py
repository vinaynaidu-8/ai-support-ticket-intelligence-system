from sqlalchemy.orm import Session

from app.models.ai_analysis import AIAnalysis


def save_ai_analysis(
    db: Session,
    ticket_id: int,
    model_name: str,
    summary: str,
    suggested_category: str,
    suggested_priority: str,
    suggested_response: str,
    detected_issue: str,
    recommended_action: str,
    confidence: float,
    human_escalation: bool,
    customer_response: str,
) -> AIAnalysis:

    analysis = AIAnalysis(
        ticket_id=ticket_id,
        model_name=model_name,
        summary=summary,
        suggested_category=suggested_category,
        suggested_priority=suggested_priority,
        suggested_response=suggested_response,
        detected_issue=detected_issue,
        recommended_action=recommended_action,
        confidence=confidence,
        human_escalation=human_escalation,
        customer_response=customer_response,
    )

    try:
        db.add(analysis)
        db.commit()
        db.refresh(analysis)

    except Exception:
        db.rollback()
        raise

    return analysis