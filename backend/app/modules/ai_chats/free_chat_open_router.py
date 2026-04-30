"""OpenRouter API integration for free AI models."""

import logging
import httpx
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def send_to_openrouter(message: str, model_name: str) -> str:
    """Send a message to OpenRouter API and get the AI response.
    
    Args:
        message: The user's message
        model_name: The AI model to use (real model name, not alias)
        
    Returns:
        str: The AI's response text
        
    Raises:
        ValueError: If API key is not configured
        httpx.HTTPError: If the API request fails
        Exception: For other errors
    """
    api_key = getattr(settings, 'OPENROUTER_COPILOT_AI_CHAT_KEY_FREE', None)
    print(api_key)

    if not api_key:
        logger.error("OpenRouter API key not configured")
        raise ValueError("OpenRouter API key not configured")
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://copilot-ai-chat.com",  # Required by OpenRouter
        "X-Title": "Copilot AI Chat",  # Required by OpenRouter
    }
    
    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "user",
                "content": message
            }
        ]
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            if "choices" not in data or len(data["choices"]) == 0:
                logger.error("Invalid response from OpenRouter: %s", data)
                raise ValueError("Invalid response from OpenRouter API")
            
            ai_response = data["choices"][0]["message"]["content"]
            logger.info("Successfully received response from OpenRouter for model %s", model_name)
            return ai_response
            
    except httpx.HTTPStatusError as e:
        logger.error("OpenRouter API error: %s - %s", e.response.status_code, e.response.text)
        error_detail = e.response.text
        raise Exception(f"OpenRouter API error: {error_detail}")
    except httpx.RequestError as e:
        logger.error("OpenRouter request error: %s", e)
        raise Exception(f"Failed to connect to OpenRouter: {str(e)}")
    except Exception as e:
        logger.error("Unexpected error calling OpenRouter: %s", e)
        raise
