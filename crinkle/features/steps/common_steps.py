from behave import given, when, then
from django.test import Client

# Shared steps used in history/education files

@given('the app is running')
def step_app_running(context):
    context.client = Client()

@then('I should see a 200 response')
def step_see_200(context):
    assert context.response.status_code == 200