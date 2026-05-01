from behave import given, when, then
from django.test import Client
from django.urls import reverse
from cards.models import Card, GradeReport
from decimal import Decimal


@given('a card named "{name}" exists in the database')
def step_card_exists(context, name):
    report = GradeReport.objects.create(grade="5")
    Card.objects.create(
        user=context.user,
        name=name,
        grading_notes=report,
        picture_path="/",
        user_notes="",
        estimated_value=50,
    )


@given("there are no cards in the database")
def step_no_cards(context):
    Card.objects.all().delete()


@when("I visit the history page")
def step_visit_history(context):
    context.response = context.client.get(reverse("history"))


@then('I should see "{text}" on the history page')
def step_see_text(context, text):
    assert text == context.response.data['cards'][0]['name']
