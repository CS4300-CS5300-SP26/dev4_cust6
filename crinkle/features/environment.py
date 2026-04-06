import os
import tempfile
from django.test import Client, override_settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crinkle.settings')


def before_scenario(context, scenario):
    context.client = Client()
    context.temp_media = tempfile.TemporaryDirectory()
    context.media_override = override_settings(MEDIA_ROOT=context.temp_media.name)
    context.media_override.enable()


def after_scenario(context, scenario):
    if hasattr(context, 'media_override'):
        context.media_override.disable()
    if hasattr(context, 'temp_media'):
        context.temp_media.cleanup()
