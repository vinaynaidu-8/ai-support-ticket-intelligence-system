from app.services.tools.tool_executor import execute_tool


if __name__ == "__main__":
    result = execute_tool(
        tool_name="get_service_health",
        arguments={"service_name": "api"},
    )

    print("Tool result:")
    print(result)