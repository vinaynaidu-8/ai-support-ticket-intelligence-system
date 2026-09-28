from sqlalchemy.orm import Session

from app.models.ai_analysis import AIAnalysis
from app.models.ticket import Ticket
from app.services.ai_analysis import save_ai_analysis
from app.services.llm.gemini import analyze_ticket
from app.services.rag.context import build_context
from app.services.rag.search import retrieve_knowledge
from app.services.workflow.support_workflow import decide_next_step


def analyze_and_store_ticket(
    db: Session,
    ticket: Ticket,
) -> AIAnalysis:
    query = (
        f"Subject: {ticket.subject}\n"
        f"Description: {ticket.description}\n"
        f"Category: {ticket.category}\n"
        f"Priority: {ticket.priority}"
    )

    # Workflow stage 1:
    # Retrieve authorized company knowledge.
    results = retrieve_knowledge(
        db=db,
        query=query,
        candidate_k=10,
        final_k=5,
    )

    # Workflow stage 2:
    # Build the context supplied to the LLM.
    context = build_context(results)

    # Workflow stage 3:
    # Generate structured AI analysis.
    analysis = analyze_ticket(
        subject=ticket.subject,
        description=ticket.description,
        category=ticket.category,
        priority=ticket.priority,
        context=context,
    )

    # Workflow stage 4:
    # Application decides whether human review is required.
    workflow_decision = decide_next_step(analysis)

    # Keep the existing AI result unchanged.
    # The workflow decision currently determines the processing path
    # but does not automatically perform operational actions.
    if workflow_decision.value == "human_review":
        analysis.human_escalation = True

    return save_ai_analysis(
        db=db,
        ticket_id=ticket.id,
        model_name="gemini-3.6-flash",
        summary=analysis.summary,
        suggested_category=analysis.suggested_category,
        suggested_priority=analysis.suggested_priority,
        suggested_response=analysis.suggested_response,
        detected_issue=analysis.detected_issue,
        recommended_action=analysis.recommended_action,
        confidence=analysis.confidence,
        human_escalation=analysis.human_escalation,
        customer_response=analysis.customer_response,
    )