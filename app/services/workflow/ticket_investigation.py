from typing import Any

from sqlalchemy.orm import Session

from app.models.ticket import Ticket
from app.services.ai_analysis import save_ai_analysis
from app.services.llm.gemini import analyze_ticket
from app.services.rag.context import build_context
from app.services.rag.search import retrieve_knowledge
from app.services.tools.tool_executor import execute_tool


MAX_TOOL_CALLS = 3


def run_ticket_investigation(
    db: Session,
    ticket: Ticket,
    user_role: str,
) -> dict[str, Any]:
    """
    Run a bounded support-ticket investigation workflow.

    The application controls:
    - RAG retrieval
    - model invocation
    - tool authorization
    - tool execution
    - maximum tool calls

    The LLM does not receive permission to bypass application authorization.
    """

    query = (
        f"Subject: {ticket.subject}\n"
        f"Description: {ticket.description}\n"
        f"Category: {ticket.category}\n"
        f"Priority: {ticket.priority}"
    )

    # Step 1: Retrieve authorized company knowledge.
    results = retrieve_knowledge(
        db=db,
        query=query,
        candidate_k=10,
        final_k=5,
    )
    context = build_context(results)

    # Step 2: Perform the existing structured ticket analysis.
    analysis = analyze_ticket(
        subject=ticket.subject,
        description=ticket.description,
        category=ticket.category,
        priority=ticket.priority,
        context=context,
    )

    tool_results: list[dict[str, Any]] = []

    # Step 3: Controlled workflow decision.
    #
    # We intentionally do not let the model execute arbitrary tools here.
    # For this first production-oriented workflow, tool selection is based
    # on explicit application rules and the structured analysis result.
    #
    # If the analysis indicates escalation, create an escalation only when
    # the authenticated user's role is authorized to do so.
    if analysis.human_escalation:
        if len(tool_results) >= MAX_TOOL_CALLS:
            raise RuntimeError("Maximum tool-call limit reached.")

        escalation_result = execute_tool(
            tool_name="create_escalation",
            arguments={
                "ticket_id": ticket.id,
                "reason": analysis.recommended_action,
            },
            user_role=user_role,
        )
        tool_results.append(
            {
                "tool": "create_escalation",
                "result": escalation_result,
            }
        )

    # Step 4: Persist the structured AI result.
    stored_analysis = save_ai_analysis(
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

    return {
        "analysis": stored_analysis,
        "tool_results": tool_results,
        "workflow_status": "completed",
    }
