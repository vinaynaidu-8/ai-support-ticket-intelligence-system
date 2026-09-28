from typing import Any

from google import genai
from google.genai import types

from app.config.settings import settings
from app.services.tools.tool_executor import execute_tool


client = genai.Client(api_key=settings.gemini_api_key)

MODEL_NAME = "gemini-3.6-flash"


TOOL_DECLARATIONS = [
    {
        "name": "get_service_health",
        "description": (
            "Gets the current health status of a simulated AcmeCloud service. "
            "Use this when current service availability information is needed."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "service_name": {
                    "type": "string",
                    "description": (
                        "Name of the service to check. "
                        "Examples: api, database, authentication."
                    ),
                }
            },
            "required": ["service_name"],
        },
    },
    {
        "name": "get_account_status",
        "description": (
            "Gets the current status of a simulated customer account. "
            "Use this when account state needs to be verified."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string",
                    "description": "Customer account identifier.",
                }
            },
            "required": ["account_id"],
        },
    },
    {
        "name": "get_database_status",
        "description": (
            "Gets the current status of the simulated AcmeCloud database."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
]


def run_tool_calling(prompt: str) -> str:
    """
    Demonstrates the manual Gemini function-calling loop.

    1. Send prompt + tool declarations to Gemini.
    2. Inspect the requested function call.
    3. Execute the function through our tool executor.
    4. Send the function result back to Gemini.
    5. Return Gemini's final response.
    """

    tools = types.Tool(
        function_declarations=TOOL_DECLARATIONS
    )

    config = types.GenerateContentConfig(
        tools=[tools],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True
        ),
    )

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt)
            ],
        )
    ]

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=contents,
        config=config,
    )

    function_calls = response.function_calls

    if not function_calls:
        return response.text

    for function_call in function_calls:
        print("\nGemini requested tool:")
        print(f"Tool: {function_call.name}")
        print(f"Arguments: {function_call.args}")

        result = execute_tool(
            tool_name=function_call.name,
            arguments=function_call.args,
            user_role="support_agent",
        )

        print("Tool result:")
        print(result)

        contents.append(response.candidates[0].content)

        function_response_part = types.Part.from_function_response(
            name=function_call.name,
            response={
                "result": result,
            },
        )

        contents.append(
            types.Content(
                role="user",
                parts=[function_response_part],
            )
        )

    final_response = client.models.generate_content(
        model=MODEL_NAME,
        contents=contents,
        config=config,
    )

    return final_response.text