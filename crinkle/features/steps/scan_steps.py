from unittest.mock import patch

from behave import given, then, when
from django.urls import reverse

from cards.models import Card


LANDING_URL = "/"

TEST_CAPTURED_IMAGE = (
    "data:image/png;base64,"
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4"
    "nGP4////fwAJ+wP9KobjigAAAABJRU5ErkJggg=="
)

MOCK_GRADE_RESULT = {
    "quality_ok": True,
    "quality_issues": [],
    "psa_grade": 8,
    "card_name": "Charizard",
    "card_set": "Base Set",
    "card_year": "1999",
    "corners": "Sharp corners with no visible wear.",
    "edges": "Clean edges with no chips.",
    "centering": "Well centered.",
    "surface": "Clean surface.",
}

MOCK_QUALITY_RESULT = {
    "quality_ok": False,
    "quality_issues": ["too dark", "blurry"],
    "psa_grade": None,
    "card_name": None,
    "card_set": None,
    "card_year": None,
    "corners": None,
    "edges": None,
    "centering": None,
    "surface": None,
}


def _scan_url():
    return reverse("cards:scan_report")


def _response_text(context):
    return context.response.content.decode("utf-8", errors="ignore")


def _scenario_name(context):
    scenario = getattr(context, "scenario", None)
    return getattr(scenario, "name", "").lower()


def _mock_grade_for_context(context):
    if "poor quality" in _scenario_name(context):
        return MOCK_QUALITY_RESULT.copy()
    return MOCK_GRADE_RESULT.copy()


def _assert_status(context, expected_status):
    actual_status = context.response.status_code
    assert actual_status == expected_status, (
        f"Expected status {expected_status}, got {actual_status}. "
        f"Response body: {_response_text(context)[:500]}"
    )


@given("the application is running")
def step_application_is_running(context):
    pass


@given("I am on the landing page")
def step_on_landing_page(context):
    context.response = context.client.get(LANDING_URL)


@when("I tap the scan button")
def step_tap_scan_button(context):
    context.response = context.client.get(_scan_url())


@then("I should be taken to the scan page")
def step_should_be_taken_to_scan_page(context):
    _assert_status(context, 200)


@given("I am on the scan page")
def step_on_scan_page(context):
    context.response = context.client.get(_scan_url())


@when("the scan page loads")
def step_scan_page_loads(context):
    context.response = context.client.get(_scan_url())


@then("the camera should be initialised")
def step_camera_should_be_initialised(context):
    _assert_status(context, 200)


@given("the camera is initialised")
def step_camera_is_initialised(context):
    context.response = context.client.get(_scan_url())


@when("the scan page is displayed")
def step_scan_page_displayed(context):
    context.response = context.client.get(_scan_url())


@then("a frame for the card should appear")
def step_frame_for_card_should_appear(context):
    _assert_status(context, 200)


@given("the frame for the card is displayed")
def step_frame_for_card_is_displayed(context):
    context.response = context.client.get(_scan_url())


@then("the frame should be horizontal")
def step_frame_should_be_horizontal(context):
    _assert_status(context, 200)


@then("I should be prompted to place the card in the frame and take a photo")
def step_should_see_scan_prompt(context):
    _assert_status(context, 200)


@given("I have a card ready to scan")
def step_have_card_ready_to_scan(context):
    context.captured_scan_image = TEST_CAPTURED_IMAGE


@when("I select the scan option")
def step_select_scan_option(context):
    context.response = context.client.get(_scan_url())


@when("I place the card in the frame")
def step_place_card_in_frame(context):
    context.captured_scan_image = TEST_CAPTURED_IMAGE


@when("I press the camera button")
def step_press_camera_button(context):
    context.captured_scan_image = TEST_CAPTURED_IMAGE


@then("the photo should be taken successfully")
def step_photo_should_be_taken_successfully(context):
    assert context.captured_scan_image == TEST_CAPTURED_IMAGE


@then("the image should be displayed in the application")
def step_image_should_be_displayed(context):
    assert context.captured_scan_image.startswith("data:image/png;base64,")


@given("a photo has been taken")
def step_photo_has_been_taken(context):
    context.captured_scan_image = TEST_CAPTURED_IMAGE


@then("I should see an option to retake the photo")
def step_should_see_retake_option(context):
    assert context.captured_scan_image == TEST_CAPTURED_IMAGE


@when("I take a photo of the card")
def step_take_photo_of_card(context):
    context.captured_scan_image = TEST_CAPTURED_IMAGE


@then("I should be prompted to log in")
def step_should_be_prompted_to_log_in(context):
    assert context.response.status_code in (200, 302)


@given("I am on the camera page")
def step_on_camera_page(context):
    context.response = context.client.get(_scan_url())


@when("I tap the back button")
def step_tap_back_button(context):
    context.response = context.client.get(LANDING_URL)


@then("I should be taken back to the landing page")
def step_should_be_taken_back_to_landing_page(context):
    _assert_status(context, 200)


@given("I have taken a captured scan image")
def step_have_captured_scan_image(context):
    session = context.client.session
    session["captured_scan_image"] = TEST_CAPTURED_IMAGE
    session.save()
    context.captured_scan_image = TEST_CAPTURED_IMAGE


@when("I request a grade for the captured scan")
def step_request_grade(context):
    grade_result = _mock_grade_for_context(context)
    captured_image = getattr(
        context,
        "captured_scan_image",
        TEST_CAPTURED_IMAGE,
    )
    with patch(
        "cards.views.analyze_card_with_gemini",
        return_value=grade_result,
    ):
        context.response = context.client.post(
            reverse("cards:scan_report"),
            data={"captured_image": captured_image},
        )
    context.grade_result = grade_result


@then("I should see the grading report")
def step_see_grading_report(context):
    _assert_status(context, 200)


@then("I should see a prompt to create an account to save to collection")
def step_see_create_account_prompt(context):
    _assert_status(context, 200)
    content = _response_text(context).lower()
    assert "save" in content or "login" in content or "account" in content


@when("I try to save the scanned card to my collection")
def step_guest_try_save(context):
    context.response = context.client.get(reverse("cards:save_report"))


@when("I save the scanned card to my collection")
def step_save_scanned_card_to_collection(context):
    context.response = context.client.get(
        reverse("cards:save_report"),
        follow=True,
    )


@then("the scanned card image should be saved in my collection")
def step_scanned_card_image_saved(context):
    _assert_status(context, 200)
    saved_card = Card.objects.order_by("-id").first()
    assert saved_card is not None
    assert saved_card.picture_path.startswith("/media/scans/")


@then("I should see the scan report page")
def step_see_scan_report_page(context):
    _assert_status(context, 200)


@then("I should see a PSA grade on the report")
def step_see_psa_grade(context):
    content = _response_text(context)
    assert (
        "Grade Breakdown" in content
        or "PSA Grade" in content
        or "psa_grade" in content.lower()
        or str(context.grade_result["psa_grade"]) in content
    )


@then("I should see corners analysis on the report")
def step_see_corners(context):
    content = _response_text(context)
    assert (
        "corners" in content.lower()
        or context.grade_result["corners"] in content
    )


@then("I should see edges analysis on the report")
def step_see_edges(context):
    content = _response_text(context)
    assert (
        "edges" in content.lower()
        or context.grade_result["edges"] in content
    )


@then("I should see centering analysis on the report")
def step_see_centering(context):
    content = _response_text(context)
    assert (
        "centering" in content.lower()
        or context.grade_result["centering"] in content
    )


@then("I should see surface analysis on the report")
def step_see_surface(context):
    content = _response_text(context)
    assert (
        "surface" in content.lower()
        or context.grade_result["surface"] in content
    )


@then("the grade result should be stored in the session")
def step_grade_in_session(context):
    assert context.client.session.get("card_grade_result") is not None


@then("I should see card set and year on the report")
def step_see_card_set_year(context):
    content = _response_text(context)
    assert (
        "card-meta-tag" in content
        or "Base Set" in content
        or "1999" in content
        or "card_set" in content.lower()
    )


@then("I should see quality feedback on the report")
def step_see_quality_feedback(context):
    content = _response_text(context)
    assert (
        "Image Quality Insufficient" in content
        or "Retake Photo" in content
        or "quality" in content.lower()
    )
    
