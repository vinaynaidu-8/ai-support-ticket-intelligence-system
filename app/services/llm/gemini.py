import json

from google import genai

from app.config.settings import settings
from app.schemas.ai_analysis import AIAnalysis


client = genai.Client(api_key=settings.gemini_api_key)


def analyze_ticket(
    subject: str,
    description: str,
    category: str,
    priority: str,
) -> AIAnalysis:

    prompt = f"""
You are an AI support assistant.

Analyze the following customer support ticket.

Ticket subject:
{subject}

Ticket description:
{description}

Current category:
{category}

Current priority:
{priority}

Return a JSON object containing exactly these fields:

- summary: concise summary of the customer's issue
- suggested_category: recommended category
- suggested_priority: recommended priority
- suggested_response: professional response that a support agent can review

Do not include markdown or code fences.
Do not claim that you performed actions you cannot actually perform.
"""

    try:
        interaction = client.interactions.create(
            model="gemini-3.6-flash",
            input=prompt,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": AIAnalysis.model_json_schema(),
            },
        )

        result = json.loads(interaction.output_text)

        return AIAnalysis.model_validate(result)

    except Exception as e:
        raise RuntimeError(
            f"Ticket AI analysis failed: {e}"
        ) from e