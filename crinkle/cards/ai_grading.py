import json
import urllib.request
import urllib.error
from django.conf import settings


def analyze_card_with_gemini(image_data_url):
    """
    Send a Pokemon card image to OpenRouter and get back a PSA grade analysis.
    """
    api_key = settings.GEMINI_API_KEY

    if ";base64," not in image_data_url:
        print("AI ERROR: no base64 data in image")
        return _fallback_grade()

    header, encoded = image_data_url.split(";base64,", 1)
    mime_type = header.replace("data:", "") if "data:" in header else "image/jpeg"

    prompt = """You are a professional Pokemon card grader. Analyze this Pokemon
            card image and provide:
1. An estimated PSA grade from 1 to 10 (whole numbers only)
2. The Pokemon card name if visible
3. Notes on each of these 4 criteria (1-2 sentences each):
   - Corners: any wear, bending, or damage
   - Edges: any chips, nicks, or roughness
   - Centering: how centered the image is on the card
   - Surface: any scratches, print lines, or stains

Respond ONLY in this exact JSON format with no extra text:
{
  "psa_grade": 8,
  "card_name": "Charizard",
  "corners": "Corners appear sharp with minimal wear.",
  "edges": "Edges are clean with no visible chips.",
  "centering": "Centering is slightly off to the left.",
  "surface": "Surface is clean with no visible scratches."
}"""

    payload = json.dumps(
        {
            "model": "meta-llama/llama-4-maverick",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime_type};base64,{encoded}"},
                        },
                    ],
                }
            ],
        }
    ).encode("utf-8")

    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            text = result["choices"][0]["message"]["content"]
            text = text.strip().strip("```json").strip("```").strip()
            print(f"AI RESPONSE: {text}")
            return json.loads(text)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"AI HTTP ERROR {e.code}: {body}")
        return _fallback_grade()
    except Exception as e:
        print(f"AI ERROR: {e}")
        return _fallback_grade()


def _fallback_grade():
    return {
        "psa_grade": 7,
        "card_name": "Unknown Card",
        "corners": "Could not analyze corners.",
        "edges": "Could not analyze edges.",
        "centering": "Could not analyze centering.",
        "surface": "Could not analyze surface.",
    }
