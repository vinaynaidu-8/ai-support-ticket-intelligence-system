from typing import Any


def get_service_health(service_name: str) -> dict[str, Any]:
    services = {
        "api": {
            "service": "api",
            "status": "operational",
            "message": "API service is operating normally.",
        },
        "database": {
            "service": "database",
            "status": "operational",
            "message": "Database service is operating normally.",
        },
        "authentication": {
            "service": "authentication",
            "status": "operational",
            "message": "Authentication service is operating normally.",
        },
    }

    return services.get(
        service_name,
        {
            "service": service_name,
            "status": "unknown",
            "message": "Service was not found in the simulated environment.",
        },
    )


def get_account_status(account_id: str) -> dict[str, Any]:
    return {
        "account_id": account_id,
        "status": "active",
        "locked": False,
        "message": "Account is active and not locked.",
    }


def get_database_status() -> dict[str, Any]:
    return {
        "service": "database",
        "status": "operational",
        "connections": 42,
        "message": "Database is accepting connections normally.",
    }


def restart_test_service(service_name: str) -> dict[str, Any]:
    """
    Simulated write operation.

    This does NOT restart a real service.
    """

    return {
        "service": service_name,
        "action": "restart",
        "status": "completed",
        "environment": "test",
        "message": (
            f"Simulated restart of test service '{service_name}' "
            "completed successfully."
        ),
    }


def reset_test_account(account_id: str) -> dict[str, Any]:
    """
    Simulated account reset operation.
    """

    return {
        "account_id": account_id,
        "action": "reset",
        "status": "completed",
        "environment": "test",
        "message": (
            f"Simulated reset of test account '{account_id}' "
            "completed successfully."
        ),
    }


def create_escalation(
    ticket_id: int,
    reason: str,
) -> dict[str, Any]:
    """
    Simulated escalation operation.
    """

    return {
        "ticket_id": ticket_id,
        "action": "create_escalation",
        "status": "created",
        "reason": reason,
        "environment": "test",
        "message": "Simulated escalation created successfully.",
    }