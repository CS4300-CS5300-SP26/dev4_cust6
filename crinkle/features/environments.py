import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crinkle.settings')


def before_scenario(context, scenario):
    from django.test import Client
    context.client = Client()


def after_scenario(context, scenario):
    pass