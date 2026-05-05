from behave import given, then, when

from submission.models import Submission


START_URL = "/submission/start/"
DETAILS_URL = "/submission/details/"
CHECKOUT_URL = "/submission/checkout/"


def _content(response):
    return response.content.decode("utf-8", errors="ignore")


def _location(response):
    return response.get("Location", "")


def _debug_response(response):
    body = _content(response)[:500]
    location = _location(response)
    return (
        f"status={response.status_code}, "
        f"location={location!r}, body={body!r}"
    )


def _get_first_ok(context, urls):
    last_response = None
    for url in urls:
        response = context.client.get(url, follow=True)
        last_response = response
        if response.status_code == 200:
            context.response = response
            return response
    context.response = last_response
    return last_response


@given("I am on the submission start page")
def step_on_start_page(context):
    context.response = context.client.get(START_URL)


@given("I am on the details page with session data")
def step_on_details_page(context):
    session = context.client.session
    session["submission_service"] = "PSA"
    session["submission_card_name"] = "Charizard Base Set"
    session.save()
    context.response = context.client.get(DETAILS_URL)


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
    )


@when('I enter card name "{card_name}" and select service "{service}"')
def step_enter_card_and_service(context, card_name, service):
    context.post_data = {
        "card_name": card_name,
        "grading_service": service,
        "service": service,
    }


@when("I submit the start form")
def step_submit_start(context):
    context.response = context.client.post(START_URL, context.post_data)


@when("I fill in all shipping and payment details")
def step_fill_details(context):
    context.post_data = {
        "card_name": "Charizard Base Set",
        "grading_service": "PSA",
        "service": "PSA",
        "full_name": "Naz Siavash",
        "address": "123 Main St",
        "city": "Salt Lake City",
        "state": "UT",
        "zip_code": "84101",
    }


@when("I submit the details form")
def step_submit_details(context):
    context.response = context.client.post(DETAILS_URL, context.post_data)


@when("I submit the details form with missing fields")
def step_submit_details_missing(context):
    context.response = context.client.post(DETAILS_URL, {})


@when("I visit the confirmation page for that submission")
def step_visit_confirmation(context):
    submission_id = context.submission.pk
    _get_first_ok(
        context,
        [
            f"/submission/confirmation/{submission_id}/",
            f"/submission/checkout/{submission_id}/",
            CHECKOUT_URL,
        ],
    )


@then("I should be on the details page")
def step_on_details(context):
    if context.response.status_code in (301, 302):
        location = _location(context.response)
        assert DETAILS_URL in location, _debug_response(context.response)
        return

    assert context.response.status_code == 200, _debug_response(
        context.response
    )
    assert "detail" in _content(context.response).lower(), _debug_response(
        context.response
    )


@then("I should see the confirmation page")
def step_see_confirmation(context):
    if context.response.status_code in (301, 302):
        location = _location(context.response)
        assert (
            "checkout" in location or "confirmation" in location
        ), _debug_response(context.response)
        context.response = context.client.get(location, follow=True)
        return

    assert context.response.status_code == 200, _debug_response(
        context.response
    )


@then("the submission should exist in the database")
def step_submission_exists_db(context):
    assert Submission.objects.filter(card_name="Charizard Base Set").exists()


@then('the confirmation page shows "{card_name}"')
def step_confirmation_shows_card(context, card_name):
    assert card_name in _content(context.response), _debug_response(
        context.response
    )


@then('the confirmation page shows service "{service}"')
def step_confirmation_shows_service(context, service):
    assert service in _content(context.response), _debug_response(
        context.response
    )


@then("I should stay on the details page")
def step_stay_on_details(context):
    assert context.response.status_code == 200, _debug_response(
        context.response
    )


@then("no submission should be created")
def step_no_submission(context):
    assert not Submission.objects.exists()
