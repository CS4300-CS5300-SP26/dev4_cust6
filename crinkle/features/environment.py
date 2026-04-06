import os
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crinkle.settings')


def before_scenario(context, scenario):
    context.client = Client()


def after_scenario(context, scenario):
    pass
