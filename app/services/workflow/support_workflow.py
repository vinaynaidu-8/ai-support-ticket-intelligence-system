from enum import Enum

from app.models.ai_analysis import AIAnalysis


class WorkflowDecision(str, Enum):
    AGENT_REVIEW = "agent_review"
    HUMAN_REVIEW = "human_review"


CONFIDENCE_THRESHOLD = 0.70


def decide_next_step(analysis: AIAnalysis) -> WorkflowDecision:
    """
    Decide the next workflow step using application-level rules.

    The LLM provides recommendations and confidence.
    The application controls the workflow decision.
    """

    if analysis.human_escalation:
        return WorkflowDecision.HUMAN_REVIEW

    if analysis.confidence < CONFIDENCE_THRESHOLD:
        return WorkflowDecision.HUMAN_REVIEW

    return WorkflowDecision.AGENT_REVIEW