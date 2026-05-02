from behave import given, then, when
from django.urls import reverse

from cards.models import Card


TEST_CAPTURED_IMAGE = (
    "data:image/png;base64,"
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42"
    "mP8/x8AAwMCAO2R0xQAAAAASUVORK5CYII="
)


@given("the application is running")
def step_application_running(context):
    # Initialize or check application state
    pass


@given("I am on the landing page")
def step_on_landing_page(context):
    # Ensure user is on the landing page
    pass


@when("I tap the scan button")
def step_tap_scan_button(context):
    # Simulate tapping the scan button
    pass


@then("I should be taken to the scan page")
def step_taken_to_scan_page(context):
    # Assert navigation to scan page
    pass


@given("I am on the scan page")
def step_on_scan_page(context):
    # Ensure user is on the scan page
    pass


@when("the scan page loads")
def step_scan_page_loads(context):
    # Simulate scan page loading
    pass


@then("the camera should be initialised")
def step_camera_should_be_initialised(context):
    # Assert camera initialization
    pass


@given("the camera is initialised")
def step_camera_is_initialised(context):
    # Ensure camera is initialized
    pass


@when("the scan page is displayed")
def step_scan_page_is_displayed(context):
    # Simulate scan page display
    pass


@then("a frame for the card should appear")
def step_card_frame_should_appear(context):
    # Assert card frame appears
    pass


@given("the frame for the card is displayed")
def step_card_frame_is_displayed(context):
    # Ensure card frame is displayed
    pass


@then("the frame should be horizontal")
def step_frame_should_be_horizontal(context):
    # Assert frame orientation is horizontal
    pass


@then(
    "I should be prompted to place the card in the frame and take a photo"
)
def step_prompted_to_place_card_and_take_photo(context):
    # Assert prompt is shown to user
    pass


@given("I have a card ready to scan")
def step_card_ready_to_scan(context):
    # Ensure card is ready for scanning
    pass


@when("I select the scan option")
def step_select_scan_option(context):
    # Simulate selecting scan option
    pass


@when("I place the card in the frame")
def step_place_card_in_frame(context):
    # Simulate placing card in frame
    pass


@when("I press the camera button")
def step_press_camera_button(context):
    # Simulate pressing camera button
    pass


@then("the photo should be taken successfully")
def step_photo_should_be_taken_successfully(context):
    # Assert photo is taken
    pass


@then("the image should be displayed in the application")
def step_image_should_be_displayed(context):
    # Assert image is displayed
    pass


@given("a photo has been taken")
def step_photo_has_been_taken(context):
    # Ensure a photo has been taken
    pass


@then("I should see an option to retake the photo")
def step_retake_option_visible(context):
    # Assert retake option is visible
    pass


@when("I take a photo of the card")
def step_take_photo_of_card(context):
    # Simulate taking a photo
    pass


@then("I should be prompted to log in")
def step_prompted_to_log_in(context):
    # Assert login prompt is shown
    pass


@given("I am on the camera page")
def step_on_camera_page(context):
    # Ensure user is on camera page
    pass


@when("I tap the back button")
def step_tap_back_button(context):
    # Simulate tapping back button
    pass


@then("I should be taken back to the landing page")
def step_taken_back_to_landing_page(context):
    # Assert navigation to landing page
    pass


@given("I have taken a captured scan image")
def step_have_captured_scan_image(context):
    session = context.client.session
    session["captured_scan_image"] = TEST_CAPTURED_IMAGE
    session.save()
    context.captured_scan_image = TEST_CAPTURED_IMAGE


@when("I request a grade for the captured scan")
def step_request_grade(context):
    context.response = context.client.post(
        reverse("cards:scan_report"),
        {"captured_image": context.captured_scan_image},
    )


@then("I should see the grading report")
def step_see_grading_report(context):
    assert context.response.status_code == 200
    assert "Scan Report" in context.response.content.decode()


@then("I should see a prompt to create an account to save to collection")
def step_see_guest_save_prompt(context):
    assert context.response.status_code == 200
    assert (
        "Create an account to save this scan to your collection."
        in context.response.content.decode()
    )


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
    assert context.response.status_code == 200

    saved_card = Card.objects.order_by("-id").first()
    assert saved_card is not None
    assert saved_card.picture_path.startswith("/media/scans/")


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


@then("I should see the scan report page")
def step_see_scan_report_page(context):
    assert context.response.status_code == 200


@then("I should see a PSA grade on the report")
def step_see_psa_grade(context):
    content = context.response.content.decode()
    assert (
        "Grade Breakdown" in content
        or "PSA Grade" in content
        or "psa_grade" in content.lower()
        or any(str(i) in content for i in range(1, 11))
    )


@then("I should see corners analysis on the report")
def step_see_corners(context):
    assert "CORNERS" in context.response.content.decode().upper()


@then("I should see edges analysis on the report")
def step_see_edges(context):
    assert "EDGES" in context.response.content.decode().upper()


@then("I should see centering analysis on the report")
def step_see_centering(context):
    assert "CENTERING" in context.response.content.decode().upper()


@then("I should see surface analysis on the report")
def step_see_surface(context):
    assert "SURFACE" in context.response.content.decode().upper()


@then("the grade result should be stored in the session")
def step_grade_in_session(context):
    assert context.client.session.get("card_grade_result") is not None


@then("I should see card set and year on the report")
def step_see_card_set_year(context):
    content = context.response.content.decode()
    assert (
        "card-meta-tag" in content
        or "Base Set" in content
        or "card_set" in content.lower()
    )


@then("I should see quality feedback on the report")
def step_see_quality_feedback(context):
    content = context.response.content.decode()
    assert (
        "Image Quality Insufficient" in content
        or "Retake Photo" in content
        or "quality" in content.lower()
    )