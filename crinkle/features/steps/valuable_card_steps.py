from behave import given, when, then
from django.urls import reverse
from django.contrib.auth.models import User

from cards.models import CardCollection, Card, GradeReport


@given("I have a collection of cards of value {value}")
def cards_of_value(context, value):
    context.collection = CardCollection.objects.create(user=context.user)

    # add 10 cards for the sake of testing
    for i in range(10):
        notes = GradeReport.objects.create(grade="Grade")
        card = Card.objects.create(
            user=context.user,
            name="Card",
            grading_notes=notes,
            picture_path="/",
            user_notes="",
            estimated_value=value,
        )
        card.name += f"-{card.pk}"  # add card primary key as differentiator
        card.save()
        context.collection.cards.add(card)


@when("I set a value threshold of {value}")
def set_value_threshold(context, value):
    context.collection.value_threshold = value
    context.collection.save()


@then('it is "{is_valuable}" that my cards are valuable')
def view_collection(context, is_valuable):
    context.response = context.client.get(reverse("cards:collection"))

    for card in context.response.data["cards"]:
        if is_valuable == "True":
            assert card["is_valuable"]
        else:
            assert not card["is_valuable"]
