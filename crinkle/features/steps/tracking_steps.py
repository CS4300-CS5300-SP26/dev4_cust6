from behave import given, then, when
from django.contrib.auth.models import User

from tracking.models import TrackedCard


TRACKING_LIST_URL = "/tracking/"
TRACKING_ADD_URL = "/tracking/add/"
MARKET_URL = "/tracking/market/"

STATUS_MAP = {
    "Watching": "watching",
    "Submitted for Grading": "submitted",
    "Graded": "graded",
    "Sold": "sold",
    "Owned": "owned",
}

TIER_MAP = {
    "Ungraded": "ungraded",
    "PSA 1": "psa_1",
    "PSA 2": "psa_2",
    "PSA 3": "psa_3",
    "PSA 4": "psa_4",
    "PSA 5": "psa_5",
    "PSA 6": "psa_6",
    "PSA 7": "psa_7",
    "PSA 8": "psa_8",
    "PSA 9": "psa_9",
    "PSA 10": "psa_10",
}


def _content(response):
    return response.content.decode("utf-8", errors="ignore")


def _debug_response(response):
    body = _content(response)[:500]
    location = response.get("Location", "")
    return (
        f"status={response.status_code}, "
        f"location={location!r}, body={body!r}"
    )


def _ensure_user(context):
    if hasattr(context, "tracking_user"):
        return context.tracking_user

    context.tracking_user = User.objects.create_user(
        username="trackinguser",
        password="StrongPass123!",
    )
    context.client.force_login(context.tracking_user)
    return context.tracking_user


def _tracked_card_fields():
    return {field.name for field in TrackedCard._meta.fields}


def _create_tracked_card(context, **overrides):
    fields = _tracked_card_fields()
    data = {
        "card_name": overrides.pop("card_name", "Test Card"),
        "status": overrides.pop("status", "watching"),
    }

    optional_defaults = {
        "card_set": "Base Set",
        "card_year": 1999,
        "grade_tier": "ungraded",
        "notes": "",
    }
    for field_name, value in optional_defaults.items():
        if field_name in fields:
            data[field_name] = overrides.pop(field_name, value)

    if "user" in fields:
        data["user"] = overrides.pop("user", _ensure_user(context))

    data.update(overrides)
    return TrackedCard.objects.create(**data)


def _assert_status(response, expected_status):
    assert response.status_code == expected_status, _debug_response(response)


def _get_tracking_list(context, query_string=""):
    _ensure_user(context)
    context.response = context.client.get(
        f"{TRACKING_LIST_URL}{query_string}",
        follow=True,
    )
    return context.response


@given("I am on the tracking add page")
def step_on_add_page(context):
    _ensure_user(context)
    context.response = context.client.get(TRACKING_ADD_URL, follow=True)
    _assert_status(context.response, 200)


@when('I fill in card name "{name}" set "{card_set}" year "{year}"')
def step_fill_card_info(context, name, card_set, year):
    context.card_data = {
        "card_name": name,
        "card_set": card_set,
        "card_year": int(year),
        "grade_tier": "ungraded",
        "status": "watching",
        "notes": "",
    }


@when('I select grade tier "{tier}" and status "{status}"')
def step_select_tier_status(context, tier, status):
    context.card_data["grade_tier"] = TIER_MAP.get(tier, "ungraded")
    context.card_data["status"] = STATUS_MAP.get(status, "watching")


@when("I submit the tracking form")
def step_submit_form(context):
    _ensure_user(context)
    context.response = context.client.post(TRACKING_ADD_URL, context.card_data)


@when("I submit the tracking form without a card name")
def step_submit_empty_form(context):
    _ensure_user(context)
    context.response = context.client.post(
        TRACKING_ADD_URL,
        {
            "card_name": "",
            "grade_tier": "ungraded",
            "status": "watching",
            "notes": "",
        },
    )


@then("I should be redirected to the tracking list")
def step_redirected_to_list(context):
    assert context.response.status_code in (301, 302), _debug_response(
        context.response
    )
    location = context.response.get("Location", "")
    assert TRACKING_LIST_URL in location, _debug_response(context.response)


@then('I should see "{text}" in the tracking list')
def step_see_in_list(context, text):
    response = _get_tracking_list(context)
    assert text in _content(response), _debug_response(response)


@then('I should not see "{text}" in the tracking list')
def step_not_see_in_list(context, text):
    assert text not in _content(context.response), _debug_response(
        context.response
    )


@then("I should stay on the add card page")
def step_stay_on_add(context):
    _assert_status(context.response, 200)


@then("no card should be created")
def step_no_card_created(context):
    assert TrackedCard.objects.count() == 0


@given('a card "{name}" with status "{status}"')
def step_card_exists(context, name, status):
    context.last_card = _create_tracked_card(
        context,
        card_name=name,
        status=STATUS_MAP.get(status, "watching"),
    )


@given('that card was sold for "{price}"')
def step_set_sold_price(context, price):
    context.last_card.sold_price = float(price)
    context.last_card.save()


@when("I visit the tracking list")
def step_visit_list(context):
    _get_tracking_list(context)


@when('I view the detail page for "{name}"')
def step_view_detail(context, name):
    _ensure_user(context)
    card = TrackedCard.objects.get(card_name=name)
    context.response = context.client.get(
        f"{TRACKING_LIST_URL}{card.pk}/",
        follow=True,
    )


@then('I should see "{text}" on the page')
def step_see_on_page(context, text):
    content = _content(context.response)
    assert text in content or text.lower() in content.lower(), _debug_response(
        context.response
    )


@when('I filter the tracking list by "{status}"')
def step_filter_by_status(context, status):
    _get_tracking_list(context, f"?status={status}")


@when('I edit "{name}" and change status to "{new_status}"')
def step_edit_card(context, name, new_status):
    _ensure_user(context)
    card = TrackedCard.objects.get(card_name=name)
    context.response = context.client.post(
        f"{TRACKING_LIST_URL}{card.pk}/edit/",
        {
            "card_name": card.card_name,
            "card_set": getattr(card, "card_set", "Base Set"),
            "card_year": getattr(card, "card_year", 1999) or "",
            "grade_tier": getattr(card, "grade_tier", "ungraded"),
            "status": STATUS_MAP.get(new_status, "watching"),
            "notes": getattr(card, "notes", ""),
        },
    )


@then('the card "{name}" should have status "{status}"')
def step_check_status(context, name, status):
    card = TrackedCard.objects.get(card_name=name)
    assert card.status == status


@when('I delete the card "{name}"')
def step_delete_card(context, name):
    _ensure_user(context)
    card = TrackedCard.objects.get(card_name=name)
    context.response = context.client.post(
        f"{TRACKING_LIST_URL}{card.pk}/delete/"
    )


@then('"{name}" should not exist in tracking')
def step_card_not_exist(context, name):
    assert not TrackedCard.objects.filter(card_name=name).exists()


@then('the sold total should be "{total}"')
def step_check_sold_total(context, total):
    content = _content(context.response)
    whole_dollars = total.split(".")[0]
    assert f"${total}" in content or f"${whole_dollars}" in content


@given("I visit the market page")
def step_visit_market(context):
    _ensure_user(context)
    context.response = context.client.get(MARKET_URL, follow=True)


@then("I should see the market page")
def step_see_market(context):
    _assert_status(context.response, 200)


@given('a pricing entry for "{name}" in "{card_set}"')
def step_pricing_entry(context, name, card_set):
    from tracking.models import CardPricing

    CardPricing.objects.create(
        card_name=name,
        card_set=card_set,
        grade_tier="ungraded",
        price=50.00,
    )


@when('I search the market for "{query}"')
def step_search_market(context, query):
    _ensure_user(context)
    context.response = context.client.get(
        f"{MARKET_URL}?q={query}",
        follow=True,
    )


@then('I should see "{text}" in the market results')
def step_see_in_market(context, text):
    assert text in _content(context.response), _debug_response(
        context.response
    )


@when('I view pricing for "{name}" in "{card_set}"')
def step_view_pricing(context, name, card_set):
    _ensure_user(context)
    context.response = context.client.get(
        f"{MARKET_URL}pricing/?name={name}&set={card_set}",
        follow=True,
    )
