import json
import urllib.error
import urllib.request

from django.conf import settings


def analyze_card_with_gemini(image_data_url):
    """
    Send a Pokemon card image to OpenRouter and get back:
    - Quality check (is image good enough to grade?)
    - Card identification (name, set, year)
    - PSA grade + breakdown (corners, edges, centering, surface)
    """
    api_key = settings.GEMINI_API_KEY

    if ";base64," not in image_data_url:
        print("AI ERROR: no base64 data in image")
        return _fallback_grade()

    header, encoded = image_data_url.split(";base64,", 1)
    mime_type = header.replace("data:", "") if "data:" in header else "image/jpeg"

    prompt = (
        "You are a professional Pokemon card grader and identifier. Analyze "
        "this image and respond in two stages:\n\n"
        "STAGE 1 - IMAGE QUALITY CHECK:\n"
        "First, assess if the image quality is sufficient for accurate "
        "grading.\n"
        "Check for:\n"
        "- Brightness: is the image too dark or overexposed?\n"
        "- Sharpness: is the image too blurry or out of focus?\n"
        "- Framing: is the card properly centered and fully visible in the "
        "frame?\n"
        "- Subject: is this actually a Pokemon card, not a screen, digital "
        "image, or non-card object?\n\n"
        "STAGE 2 - CARD IDENTIFICATION AND GRADING:\n"
        "Only if quality is sufficient, identify and grade the card.\n\n"
        "Respond ONLY in this exact JSON format with no extra text:\n"
        "{\n"
        '  "quality_ok": true,\n'
        '  "quality_issues": [],\n'
        '  "psa_grade": 8,\n'
        '  "card_name": "Charizard",\n'
        '  "card_set": "Base Set",\n'
        '  "card_year": "1999",\n'
        '  "corners": "Corners appear sharp with minimal wear.",\n'
        '  "edges": "Edges are clean with no visible chips.",\n'
        '  "centering": "Centering is slightly off to the left.",\n'
        '  "surface": "Surface is clean with no visible scratches."\n'
        "}\n\n"
        "Rules:\n"
        "- quality_ok: true if image is good enough to grade, false "
        "otherwise\n"
        "- quality_issues: empty list if quality_ok is true; otherwise list "
        'any of: "too dark", "too bright", "blurry", '
        '"card not centered", "card not fully visible", '
        '"not a physical card", "not a pokemon card"\n'
        "- If quality_ok is false, set psa_grade to null and leave other "
        "fields as null\n"
        "- card_set: the Pokemon TCG set name, for example "
        '"Base Set", "Jungle", or "Scarlet & Violet"; use '
        '"Unknown Set" if not visible\n'
        "- card_year: the year printed on the card or estimated from the "
        'set; use "Unknown" if not visible\n'
        "- psa_grade: whole number 1-10, or null if quality_ok is false\n"
        "- All text fields should be null if quality_ok is false"
    )

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
                            "image_url": {
                                "url": f"data:{mime_type};base64,{encoded}",
                            },
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
        "quality_ok": True,
        "quality_issues": [],
        "psa_grade": 7,
        "card_name": "Unknown Card",
        "card_set": "Unknown Set",
        "card_year": "Unknown",
        "corners": "Could not analyze corners.",
        "edges": "Could not analyze edges.",
        "centering": "Could not analyze centering.",
        "surface": "Could not analyze surface.",
    }