from behave import given, when, then
from django.test import Client
from tracking.models import TrackedCard


@given('I am on the tracking add page')
def step_on_add_page(context):
    context.response = context.client.get('/tracking/add/')
    assert context.response.status_code == 200


@when('I fill in card name "{name}" set "{card_set}" year "{year}"')
def step_fill_card_info(context, name, card_set, year):
    context.card_data = {
        'card_name': name,
        'card_set': card_set,
        'card_year': int(year),
        'grade_tier': 'ungraded',
        'status': 'watching',
        'notes': '',
    }


@when('I select grade tier "{tier}" and status "{status}"')
def step_select_tier_status(context, tier, status):
    tier_map = {
        'Ungraded': 'ungraded', 'PSA 1': 'psa_1', 'PSA 2': 'psa_2',
        'PSA 3': 'psa_3', 'PSA 4': 'psa_4', 'PSA 5': 'psa_5',
        'PSA 6': 'psa_6', 'PSA 7': 'psa_7', 'PSA 8': 'psa_8',
        'PSA 9': 'psa_9', 'PSA 10': 'psa_10',
    }
    status_map = {
        'Watching': 'watching', 'Submitted for Grading': 'submitted',
        'Graded': 'graded', 'Sold': 'sold', 'Owned': 'owned',
    }
    context.card_data['grade_tier'] = tier_map.get(tier, 'ungraded')
    context.card_data['status'] = status_map.get(status, 'watching')


@when('I submit the tracking form')
def step_submit_form(context):
    context.response = context.client.post('/tracking/add/', context.card_data)


@when('I submit the tracking form without a card name')
def step_submit_empty_form(context):
    context.response = context.client.post('/tracking/add/', {
        'card_name': '',
        'grade_tier': 'ungraded',
        'status': 'watching',
        'notes': '',
    })


@then('I should be redirected to the tracking list')
def step_redirected_to_list(context):
    assert context.response.status_code == 302
    assert '/tracking/' in context.response.url


@then('I should see "{text}" in the tracking list')
def step_see_in_list(context, text):
    response = context.client.get('/tracking/')
    assert text in response.content.decode()


@then('I should not see "{text}" in the tracking list')
def step_not_see_in_list(context, text):
    assert text not in context.response.content.decode()


@then('I should stay on the add card page')
def step_stay_on_add(context):
    assert context.response.status_code == 200


@then('no card should be created')
def step_no_card_created(context):
    assert TrackedCard.objects.count() == 0


@given('a card "{name}" with status "{status}"')
def step_card_exists(context, name, status):
    status_map = {
        'Watching': 'watching', 'Submitted for Grading': 'submitted',
        'Graded': 'graded', 'Sold': 'sold', 'Owned': 'owned',
    }
    context.last_card = TrackedCard.objects.create(
        card_name=name,
        status=status_map.get(status, 'watching'),
    )


@given('that card was sold for "{price}"')
def step_set_sold_price(context, price):
    context.last_card.sold_price = float(price)
    context.last_card.save()


@when('I visit the tracking list')
def step_visit_list(context):
    context.response = context.client.get('/tracking/')


@when('I view the detail page for "{name}"')
def step_view_detail(context, name):
    card = TrackedCard.objects.get(card_name=name)
    context.response = context.client.get(f'/tracking/{card.pk}/')


@then('I should see "{text}" on the page')
def step_see_on_page(context, text):
    assert text in context.response.content.decode()


@when('I filter the tracking list by "{status}"')
def step_filter_by_status(context, status):
    context.response = context.client.get(f'/tracking/?status={status}')


@when('I edit "{name}" and change status to "{new_status}"')
def step_edit_card(context, name, new_status):
    card = TrackedCard.objects.get(card_name=name)
    status_map = {
        'Watching': 'watching', 'Submitted for Grading': 'submitted',
        'Graded': 'graded', 'Sold': 'sold', 'Owned': 'owned',
    }
    context.response = context.client.post(f'/tracking/{card.pk}/edit/', {
        'card_name': card.card_name,
        'card_set': card.card_set,
        'card_year': card.card_year or '',
        'grade_tier': card.grade_tier,
        'status': status_map.get(new_status, 'watching'),
        'notes': card.notes,
    })


@then('the card "{name}" should have status "{status}"')
def step_check_status(context, name, status):
    card = TrackedCard.objects.get(card_name=name)
    assert card.status == status


@when('I delete the card "{name}"')
def step_delete_card(context, name):
    card = TrackedCard.objects.get(card_name=name)
    context.response = context.client.post(f'/tracking/{card.pk}/delete/')


@then('"{name}" should not exist in tracking')
def step_card_not_exist(context, name):
    assert not TrackedCard.objects.filter(card_name=name).exists()


@then('the sold total should be "{total}"')
def step_check_sold_total(context, total):
    content = context.response.content.decode()
    assert f'${total}' in content or f'${total.split(".")[0]}' in content


@given('I visit the market page')
def step_visit_market(context):
    context.response = context.client.get('/tracking/market/')


@then('I should see the market page')
def step_see_market(context):
    assert context.response.status_code == 200


@given('a pricing entry for "{name}" in "{card_set}"')
def step_pricing_entry(context, name, card_set):
    from tracking.models import CardPricing
    CardPricing.objects.create(
        card_name=name, card_set=card_set,
        grade_tier='ungraded', price=50.00,
    )


@when('I search the market for "{query}"')
def step_search_market(context, query):
    context.response = context.client.get(f'/tracking/market/?q={query}')


@then('I should see "{text}" in the market results')
def step_see_in_market(context, text):
    assert text in context.response.content.decode()


@when('I view pricing for "{name}" in "{card_set}"')
def step_view_pricing(context, name, card_set):
    context.response = context.client.get(
        f'/tracking/market/pricing/?name={name}&set={card_set}'
    )