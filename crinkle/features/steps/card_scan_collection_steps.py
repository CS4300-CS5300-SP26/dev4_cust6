from behave import given, then, when
from django.contrib.auth.models import User
from django.urls import reverse

from cards.models import Card, CardCollection, ScannedCard

SAMPLE_IMAGE_DATA_URL = (
    "data:image/png;base64,"
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO7Z3b0AAAAASUVORK5CYII="
)


@given("I am scanning as a guest")
def step_guest_scan(context):
    context.client.post(reverse("login_as_guest"))


@given("I am logged in for card scanning")
def step_logged_in_for_scan(context):
    user = User.objects.create_user(username="scanuser", password="safe-pass-123")
    context.user = user
    context.client.login(username="scanuser", password="safe-pass-123")


@when("I submit a captured card photo for grading")
def step_submit_photo_for_grading(context):
    context.response = context.client.post(
        reverse("cards:scan_report"),
        data={"captured_image": SAMPLE_IMAGE_DATA_URL},
    )
    context.scan = ScannedCard.objects.latest("id")


@then("I should receive a grade for the scanned card")
def step_receive_grade(context):
    assert context.response.status_code == 200
    assert context.scan.grade in context.response.content.decode()


@then("I should be told that guests cannot save cards")
def step_guest_cannot_save_message(context):
    assert "Guests can receive a grade" in context.response.content.decode()


@when("I try to save the scanned card")
def step_try_to_save_guest_scan(context):
    context.response = context.client.post(
        reverse("cards:save_report"),
        data={"scan_id": context.scan.pk},
    )


@then("the scanned card should not be saved to a collection")
def step_scan_not_saved(context):
    assert context.response.status_code == 403
    assert Card.objects.count() == 0


@when("I save the scanned card to my collection")
def step_save_scan_to_collection(context):
    context.response = context.client.post(
        reverse("cards:save_report"),
        data={"scan_id": context.scan.pk},
    )


@then("the scanned card should appear in my collection")
def step_scan_saved_in_collection(context):
    assert context.response.status_code == 302
    context.saved_card = Card.objects.latest("id")
    collection = CardCollection.objects.get(user=context.user)
    assert collection.cards.filter(pk=context.saved_card.pk).exists()
    assert context.saved_card.picture_path == context.scan.picture_path
    assert context.saved_card.grading_notes.grade == context.scan.grade


@when("I delete the saved card from my collection")
def step_delete_saved_card(context):
    context.response = context.client.post(
        reverse("cards:delete_card", args=[context.saved_card.pk])
    )


@then("the saved card should be removed from my collection")
def step_saved_card_removed(context):
    assert context.response.status_code == 302
    assert not Card.objects.filter(pk=context.saved_card.pk).exists()
    collection = CardCollection.objects.get(user=context.user)
    assert collection.cards.count() == 0
