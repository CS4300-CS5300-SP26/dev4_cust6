import os
import tempfile
from unittest.mock import patch

from django.core.cache import cache
from django.test import Client, override_settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crinkle.settings")


MOCK_GRADE_RESULT = {
    "quality_ok": True,
    "quality_issues": [],
    "psa_grade": 8,
    "card_name": "Test Card",
    "card_set": "Base Set",
    "card_year": "1999",
    "corners": "Good corners.",
    "edges": "Clean edges.",
    "centering": "Centered.",
    "surface": "Clean surface.",
}


def before_all(context):
    context.rate_limit_override = override_settings(
        RATELIMIT_ENABLE=False
    )
    context.rate_limit_override.enable()
    cache.clear()


def before_scenario(context, scenario):
    cache.clear()
    context.client = Client()
    context.temp_media = tempfile.TemporaryDirectory()
    context.media_override = override_settings(
        MEDIA_ROOT=context.temp_media.name,
        MEDIA_URL="/media/",
    )
    context.media_override.enable()

    if "stub_ai" in scenario.tags:
        context.ai_patch = patch(
            "cards.views.analyze_card_with_gemini",
            return_value=MOCK_GRADE_RESULT.copy(),
        )
        context.ai_patch.start()


def after_scenario(context, scenario):
    if hasattr(context, "ai_patch"):
        context.ai_patch.stop()
        del context.ai_patch

    if hasattr(context, "media_override"):
        context.media_override.disable()
        del context.media_override

    if hasattr(context, "temp_media"):
        context.temp_media.cleanup()
        del context.temp_media

    cache.clear()


def after_all(context):
    cache.clear()

    if hasattr(context, "rate_limit_override"):
        context.rate_limit_override.disable()
        
