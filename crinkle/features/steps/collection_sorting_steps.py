from behave import given, when, then
from django.urls import reverse
from django.contrib.auth.models import User

from cards.models import CardCollection, Card, GradeReport


@given("I am logged in")
def login(context):
    username = "username"
    password = "p1234567890"
    context.user = User.objects.create_user(username=username, password=password)
    context.client.login(username=username, password=password)


@given("I have a collection of cards")
def start(context):
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
        )
        card.name += f"-{card.pk}"  # add card primary key as differentiator
        card.save()
        context.collection.cards.add(card)


@when('I sort by card "{sort_order}"')
def sort_cards(context, sort_order):
    # set sorting order before making request
    context.collection.sort_order = sort_order
    context.collection.save()

    context.response = context.client.get(reverse("cards:collection"))

    # response recieved
    assert context.response.status_code == 200


@then('my cards will be ordered by "{sort_order}"')
def check_sort(context, sort_order):

    # order a set of cards by the intended order to compare to the returned cards
    cards_correct = context.collection.ordered_collection()
    response_cards = context.response.data["cards"]

    for card in range(len(response_cards)):
        assert cards_correct[card].id == response_cards[card]["id"]
