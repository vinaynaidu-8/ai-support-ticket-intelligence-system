from app.services.tools.support_tools import (
    create_escalation,
    get_account_status,
    get_database_status,
    get_service_health,
    reset_test_account,
    restart_test_service,
)


TOOL_REGISTRY = {
    "get_service_health": get_service_health,
    "get_account_status": get_account_status,
    "get_database_status": get_database_status,
    "restart_test_service": restart_test_service,
    "reset_test_account": reset_test_account,
    "create_escalation": create_escalation,
}