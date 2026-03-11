from django.test import Client
from django.contrib.auth.models import User

def before_scenario(context, scenario):
    """set_up for behave testing initialize client and user
    """
    context.client = Client()

    username = 'username'
    password = 'p1234567890'
    context.user = User.objects.create_user(username=username, password=password)
    context.client.login(username=username, password=password)
