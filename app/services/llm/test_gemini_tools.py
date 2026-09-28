from app.services.llm.gemini_tools import run_tool_calling


if __name__ == "__main__":
    prompt = """
You are an AcmeCloud support assistant.

A customer reports that the API may be unavailable.

Before answering, determine whether you need current API service
health information. If needed, use the appropriate available tool.

After receiving the tool result, provide a concise support response.
Do not claim that you performed any action.
"""

    result = run_tool_calling(prompt)

    print("\nFinal Gemini response:")
    print(result)