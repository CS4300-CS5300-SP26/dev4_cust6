from behave import given, when, then
from django.test import Client
from home.models import Card
from decimal import Decimal

@given('the app is running')
def step_app_running(context):
    context.client = Client()

@given('a card named "{name}" exists in the database')
def step_card_exists(context, name):
    context.client = Client()
    Card.objects.create(name=name, set_name="Test Set", grade=Decimal("9.0"))

@given('there are no cards in the database')
def step_no_cards(context):
    context.client = Client()
    Card.objects.all().delete()

@when('I visit the history page')
def step_visit_history(context):
    context.response = context.client.get('/history/')

@then('I should see a 200 response')
def step_see_200(context):
    assert context.response.status_code == 200

@then('I should see "{text}" on the history page')
def step_see_text(context, text):
    assert text.encode() in context.response.content