from types import SimpleNamespace

from app.services.workflow.support_workflow import (
    WorkflowDecision,
    decide_next_step,
)


def test_high_confidence_analysis_goes_to_agent():
    analysis = SimpleNamespace(
        confidence=0.95,
        human_escalation=False,
    )

    result = decide_next_step(analysis)

    assert result == WorkflowDecision.AGENT_REVIEW


def test_explicit_escalation_goes_to_human():
    analysis = SimpleNamespace(
        confidence=0.95,
        human_escalation=True,
    )

    result = decide_next_step(analysis)

    assert result == WorkflowDecision.HUMAN_REVIEW


def test_low_confidence_goes_to_human():
    analysis = SimpleNamespace(
        confidence=0.50,
        human_escalation=False,
    )

    result = decide_next_step(analysis)

    assert result == WorkflowDecision.HUMAN_REVIEW


if __name__ == "__main__":
    test_high_confidence_analysis_goes_to_agent()
    test_explicit_escalation_goes_to_human()
    test_low_confidence_goes_to_human()

    print("All workflow tests passed.")