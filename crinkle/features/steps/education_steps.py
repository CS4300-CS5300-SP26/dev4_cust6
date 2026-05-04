from behave import when, then


@when("I visit the education page")
def step_visit_education(context):
    context.response = context.client.get("/education/")


@then('I should see "{text}" on the education page')
def step_see_text_education(context, text):
    assert text.encode() in context.response.content, (
        f'Expected "{text}" in response but did not find it'
    )
