from app.services.tools.tool_executor import execute_tool


def test_support_agent_can_read_service_health():
    result = execute_tool(
        tool_name="get_service_health",
        arguments={"service_name": "api"},
        user_role="support_agent",
    )

    assert result["status"] == "operational"


def test_support_agent_cannot_restart_service():
    try:
        execute_tool(
            tool_name="restart_test_service",
            arguments={"service_name": "api"},
            user_role="support_agent",
        )
    except PermissionError as exc:
        print("Correctly blocked support-agent write operation:")
        print(exc)
    else:
        raise AssertionError(
            "Support agent should not be allowed to restart a service."
        )


def test_support_manager_can_restart_service():
    result = execute_tool(
        tool_name="restart_test_service",
        arguments={"service_name": "api"},
        user_role="support_manager",
    )

    assert result["status"] == "completed"
    assert result["environment"] == "test"


def test_customer_cannot_use_internal_tool():
    try:
        execute_tool(
            tool_name="get_service_health",
            arguments={"service_name": "api"},
            user_role="customer",
        )
    except PermissionError as exc:
        print("Correctly blocked customer:")
        print(exc)
    else:
        raise AssertionError(
            "Customer should not be allowed to use internal tools."
        )


if __name__ == "__main__":
    test_support_agent_can_read_service_health()
    test_support_agent_cannot_restart_service()
    test_support_manager_can_restart_service()
    test_customer_cannot_use_internal_tool()

    print("\nAll authorization tests passed.")