from typing import Final


TOOL_PERMISSIONS: Final[dict[str, set[str]]] = {
    # Read-only tools
    "get_service_health": {
        "support_agent",
        "support_manager",
        "admin",
    },
    "get_account_status": {
        "support_agent",
        "support_manager",
        "admin",
    },
    "get_database_status": {
        "support_manager",
        "admin",
    },

    # Write tools
    "restart_test_service": {
        "support_manager",
        "admin",
    },
    "reset_test_account": {
        "support_manager",
        "admin",
    },
    "create_escalation": {
        "support_agent",
        "support_manager",
        "admin",
    },
}


def is_tool_allowed(tool_name: str, user_role: str) -> bool:
    allowed_roles = TOOL_PERMISSIONS.get(tool_name)

    if allowed_roles is None:
        return False

    return user_role in allowed_roles