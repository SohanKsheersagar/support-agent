"""One bounded Gemini call with validated JSON and secret-safe failures."""

import json
import os
from time import monotonic

from google import genai
from google.genai import errors, types
import httpx
from pydantic import BaseModel, ValidationError


class GatewayError(RuntimeError):
    pass


def complete(instruction: str, data: dict, schema: type[BaseModel]) -> tuple[BaseModel, dict]:
    model = os.environ.get("GEMINI_MODEL", "").strip()
    if not model:
        raise GatewayError("missing_model_configuration")
    started = monotonic()
    try:
        with genai.Client(http_options=types.HttpOptions(
            timeout=30_000, retry_options=types.HttpRetryOptions(attempts=1)
        )) as client:
            response = client.models.generate_content(
                model=model,
                contents=json.dumps(data),
                config=types.GenerateContentConfig(
                    system_instruction=instruction,
                    response_mime_type="application/json",
                    response_json_schema=schema.model_json_schema(),
                    max_output_tokens=2048,
                ),
            )
        parsed = schema.model_validate_json(response.text or "")
    except errors.APIError as error:
        # Provider messages can include request details; expose only the status code.
        raise GatewayError(f"provider_error_{error.code}") from None
    except (httpx.HTTPError, ValidationError, ValueError):
        raise GatewayError("provider_or_output_failure") from None
    usage = response.usage_metadata
    return parsed, {
        "model": model,
        "latency_ms": round((monotonic() - started) * 1000),
        "tokens_in": usage.prompt_token_count if usage else None,
        "tokens_out": usage.candidates_token_count if usage else None,
        "tokens_total": usage.total_token_count if usage else None,
    }
