from behave import given, when, then
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import UserProfile


# ── Given steps ──────────────────────────────────────────────────────────────


@given("I am on the register page")
def step_on_register_page(context):
    context.response = context.client.get(reverse("register"))
    assert context.response.status_code == 200


@given("I am on the login page")
def step_on_login_page(context):
    context.response = context.client.get(reverse("login"))
    assert context.response.status_code == 200


@given('a user "{username}" already exists')
def step_user_exists(context, username):
    User.objects.create_user(username=username, password="Pass12345!")


@given('a user "{username}" with password "{password}" exists')
def step_user_with_password_exists(context, username, password):
    user = User.objects.create_user(username=username, password=password)
    UserProfile.objects.get_or_create(user=user)


@given('I am logged in as "{username}"')
def step_logged_in(context, username):
    context.client.login(username=username, password="StrongPass123!")


@given("I am not logged in")
def step_not_logged_in(context):
    context.client.logout()


# ── When steps ───────────────────────────────────────────────────────────────


@when('I fill in username "{username}" email "{email}" password "{password}"')
def step_fill_register_form(context, username, email, password):
    context.form_data = {
        "username": username,
        "email": email,
        "password1": password,
        "password2": password,
    }


@when('I enter confirm password "{password}"')
def step_enter_confirm_password(context, password):
    context.form_data["password2"] = password


@when("I submit the registration form")
def step_submit_register(context):
    context.response = context.client.post(reverse("register"), context.form_data)


@when(
    'I submit registration with username "{username}" '
    'email "{email}" password "{password}"'
)
def step_submit_registration_inline(context, username, email, password):
    context.response = context.client.post(
        reverse("register"),
        {
            "username": username,
            "email": email,
            "password1": password,
            "password2": password,
        },
    )
    context.submitted_username = username


@when('I log in with username "{username}" and password "{password}"')
def step_login(context, username, password):
    context.response = context.client.post(
        reverse("login"),
        {
            "username": username,
            "password": password,
        },
    )


@when("I visit the profile page")
def step_visit_profile(context):
    context.response = context.client.get(reverse("profile"))


@when("I log out")
def step_logout(context):
    context.response = context.client.post(reverse("logout"))


@when("I click continue as guest")
def step_continue_as_guest(context):
    context.response = context.client.post(reverse("login_as_guest"))


# ── Then steps ───────────────────────────────────────────────────────────────


@then("I should be redirected to my profile page")
def step_redirected_to_profile(context):
    assert context.response.status_code in [301, 302]
    assert "/accounts/profile/" in context.response["Location"]


@then("I should stay on the register page")
def step_stay_on_register(context):
    assert context.response.status_code == 200


@then("I should stay on the login page")
def step_stay_on_login(context):
    assert context.response.status_code == 200


@then('a user account should exist for "{username}"')
def step_user_account_exists(context, username):
    assert User.objects.filter(username=username).exists()


@then('no account should be created for "{username}"')
def step_no_account_created(context, username):
    assert not User.objects.filter(username=username).exists()


@then('only one account should exist for "{username}"')
def step_only_one_account(context, username):
    assert User.objects.filter(username=username).count() == 1


@then('I should see my username "{username}" on the page')
def step_see_username(context, username):
    assert username in context.response.content.decode()


@then("I should be redirected to the login page")
def step_redirected_to_login(context):
    assert context.response.status_code in [301, 302]
    assert "/accounts/login/" in context.response["Location"]


@then("I should be redirected to the home page")
def step_redirected_to_home(context):
    assert context.response.status_code in [301, 302]
    assert context.response["Location"] in ["/", "http://testserver/"]


@then("I should not be able to access the profile page")
def step_cannot_access_profile(context):
    response = context.client.get(reverse("profile"))
    assert response.status_code in [301, 302]
    assert "/accounts/login/" in response["Location"]


@then("the guest session flag should be set")
def step_guest_session_flag(context):
    assert context.client.session.get("is_guest") is True
