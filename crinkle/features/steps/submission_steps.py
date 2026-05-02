from behave import given, then, when

from submission.models import Submission


@given("I am on the submission start page")
def step_on_start_page(context):
    context.response = context.client.get("/submission/start/")


@given("I am on the details page with session data")
def step_on_details_page(context):
    session = context.client.session
    session["submission_service"] = "PSA"
    session["submission_card_name"] = "Charizard Base Set"
    session.save()
    context.response = context.client.get("/submission/details/")


@given('a submission exists for card "{card_name}" with service "{service}"')
def step_submission_exists(context, card_name, service):
    context.submission = Submission.objects.create(
        card_name=card_name,
        grading_service=service,
        full_name="Test User",
        address="123 Main St",
        city="Salt Lake City",
        state="UT",
        zip_code="84101",
        card_number="4111111111111111",
        expiry="12/26",
        cvv="123",
    )


@when('I enter card name "{card_name}" and select service "{service}"')
def step_enter_card_and_service(context, card_name, service):
    context.post_data = {
        "card_name": card_name,
        "grading_service": service,
    }


@when("I submit the start form")
def step_submit_start(context):
    context.response = context.client.post(
        "/submission/start/",
        context.post_data,
    )


@when("I fill in all shipping and payment details")
def step_fill_details(context):
    context.post_data = {
        "card_name": "Charizard Base Set",
        "grading_service": "PSA",
        "full_name": "Naz Siavash",
        "address": "123 Main St",
        "city": "Salt Lake City",
        "state": "UT",
        "zip_code": "84101",
        "card_number": "4111111111111111",
        "expiry": "12/26",
        "cvv": "123",
    }


@when("I submit the details form")
def step_submit_details(context):
    context.response = context.client.post(
        "/submission/details/",
        context.post_data,
    )


@when("I submit the details form with missing fields")
def step_submit_details_missing(context):
    context.response = context.client.post("/submission/details/", {})


@when("I visit the confirmation page for that submission")
def step_visit_confirmation(context):
    context.response = context.client.get(
        f"/submission/confirmation/{context.submission.pk}/"
    )


@then("I should be on the details page")
def step_on_details(context):
    assert context.response.status_code == 302
    assert "/submission/details/" in context.response["Location"]


@then("I should see the confirmation page")
def step_see_confirmation(context):
    assert context.response.status_code == 302
    assert "/submission/confirmation/" in context.response["Location"]


@then("the submission should exist in the database")
def step_submission_exists_db(context):
    assert Submission.objects.filter(card_name="Charizard Base Set").exists()


@then('the confirmation page shows "{card_name}"')
def step_confirmation_shows_card(context, card_name):
    assert card_name.encode() in context.response.content


@then('the confirmation page shows service "{service}"')
def step_confirmation_shows_service(context, service):
    assert service.encode() in context.response.content


@then("I should stay on the details page")
def step_stay_on_details(context):
    assert context.response.status_code == 200


@then("no submission should be created")
def step_no_submission(context):
    assert not Submission.objects.exists()
    
