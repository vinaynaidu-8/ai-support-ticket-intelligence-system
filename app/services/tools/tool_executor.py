from typing import Any

from app.services.tools.registry import TOOL_REGISTRY
from app.services.tools.tool_permissions import is_tool_allowed


def execute_tool(
    tool_name: str,
    arguments: dict[str, Any],
    user_role: str,
) -> dict[str, Any]:

    if not is_tool_allowed(
        tool_name=tool_name,
        user_role=user_role,
    ):
        raise PermissionError(
            f"Role '{user_role}' is not authorized to use "
            f"tool '{tool_name}'."
        )

    tool = TOOL_REGISTRY.get(tool_name)

    if tool is None:
        raise ValueError(f"Unknown tool: {tool_name}")

    return tool(**arguments)