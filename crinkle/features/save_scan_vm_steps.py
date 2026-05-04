import os
from unittest.mock import patch

from behave import given, when, then
from django.contrib.auth.models import User
from django.urls import reverse

from cards.models import Card, CardCollection


TEST_CAPTURED_IMAGE = (
    "data:image/png;base64,"
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQ"
    "VR42mP8/x8AAwMCAO2R0xQAAAAASUVORK5CYII="
)

MOCK_GRADE_RESULT = {
    "psa_grade": 8,
    "card_name": "Charizard",
    "corners": "Sharp corners with no visible wear.",
    "edges": "Clean edges with no chips.",
    "centering": "Well centered.",
    "surface": "Clean surface.",
}


@given("I am a logged in collector for VM media saves")
def step_logged_in_collector_vm(context):
    username = "vmcollector"
    password = "StrongPass123!"
    context.user = User.objects.create_user(
        username=username, password=password
    )
    assert context.client.login(username=username, password=password)


@given("I have a captured scan image ready to save")
def step_have_captured_scan_image(context):
    session = context.client.session
    session["captured_scan_image"] = TEST_CAPTURED_IMAGE
    session.save()
    context.captured_scan_image = TEST_CAPTURED_IMAGE


@given("AI grading is stubbed for the VM media scenario")
def step_stub_ai_grading(context):
    context.ai_patch = patch(
        "cards.views.analyze_card_with_gemini", return_value=MOCK_GRADE_RESULT
    )
    context.mock_ai = context.ai_patch.start()


@when("I submit the captured scan for grading")
def step_submit_captured_scan(context):
    context.grade_response = context.client.post(
        reverse("cards:scan_report"),
        {"captured_image": context.captured_scan_image},
    )
    assert context.grade_response.status_code == 200


@when("I save the graded scan to my collection using VM media storage")
def step_save_graded_scan(context):
    context.save_response = context.client.get(
        reverse("cards:save_report"), follow=True
    )
    assert context.save_response.status_code == 200
    context.saved_card = Card.objects.latest("id")


@then("a scan image file should exist in VM media storage")
def step_scan_file_exists(context):
    assert context.saved_card.picture_path.startswith("/media/scans/")
    relative_path = context.saved_card.picture_path.replace("/media/", "", 1)
    saved_file = os.path.join(context.temp_media.name, relative_path)
    assert os.path.exists(saved_file)


@then("the saved scan should belong to my collection")
def step_saved_scan_belongs_to_collection(context):
    assert context.saved_card.user == context.user
    assert CardCollection.objects.filter(
        user=context.user, cards=context.saved_card
    ).exists()


@then("the collection page should show the saved scan image")
def step_collection_page_shows_scan(context):
    response = context.client.get(reverse("cards:collection"))
    assert response.status_code == 200
    content = response.content.decode()
    assert context.saved_card.picture_path in content
    assert context.saved_card.name in content
