import os
import tempfile
from unittest.mock import patch

from django.test import Client, override_settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crinkle.settings")


def before_scenario(context, scenario):
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
            return_value={
                "psa_grade": 8,
                "card_name": "Test Card",
                "corners": "Good corners.",
                "edges": "Clean edges.",
                "centering": "Centered.",
                "surface": "Clean surface.",
            },
        )
        context.ai_patch.start()


def after_scenario(context, scenario):
    if hasattr(context, "ai_patch"):
        context.ai_patch.stop()
    if hasattr(context, "media_override"):
        context.media_override.disable()
    if hasattr(context, "temp_media"):
        context.temp_media.cleanup()
        
