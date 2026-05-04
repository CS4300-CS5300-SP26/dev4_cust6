from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import UserProfile
from parameterized import parameterized


class RegisterViewTests(TestCase):
    """Tests for user registration"""

    def setUp(self):
        self.client = Client()
        self.url = reverse("register")

    # ── Happy paths

    def test_register_page_loads(self):
        """Register page returns 200"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")

    def test_register_valid_user(self):
        """Valid registration creates user and redirects to profile"""
        response = self.client.post(
            self.url,
            {
                "username": "testuser",
                "email": "test@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        self.assertRedirects(response, reverse("profile"))
        self.assertTrue(User.objects.filter(username="testuser").exists())

    def test_register_creates_user_profile(self):
        """Registration automatically creates a UserProfile"""
        self.client.post(
            self.url,
            {
                "username": "testuser",
                "email": "test@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        user = User.objects.get(username="testuser")
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_register_logs_user_in(self):
        """After registration the user is automatically logged in"""
        self.client.post(
            self.url,
            {
                "username": "testuser",
                "email": "test@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)

    def test_register_redirects_if_already_logged_in(self):
        """Logged-in user visiting register is redirected to profile"""
        User.objects.create_user(username="existing", password="Pass12345!")
        self.client.login(username="existing", password="Pass12345!")
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("profile"))

    # ── Sad paths

    def test_register_passwords_do_not_match(self):
        """Mismatched passwords show form errors"""
        response = self.client.post(
            self.url,
            {
                "username": "testuser",
                "email": "test@example.com",
                "password1": "StrongPass123!",
                "password2": "WrongPass999!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="testuser").exists())

    def test_register_duplicate_username(self):
        """Duplicate username shows error and does not create second user"""
        User.objects.create_user(username="testuser", password="Pass12345!")
        response = self.client.post(
            self.url,
            {
                "username": "testuser",
                "email": "another@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username="testuser").count(), 1)

    def test_register_missing_fields(self):
        """Empty form submission stays on register page"""
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.all().exists())

    # ── Parametrized: invalid registration inputs

    @parameterized.expand(
        [
            ("weak_password", "testuser", "test@test.com", "123", "123"),
            (
                "password_mismatch",
                "testuser",
                "test@test.com",
                "StrongPass123!",
                "Different1!",
            ),
            (
                "empty_username",
                "",
                "test@test.com",
                "StrongPass123!",
                "StrongPass123!",
            ),
            (
                "empty_email",
                "testuser",
                "",
                "StrongPass123!",
                "StrongPass123!",
            ),
            (
                "invalid_email",
                "testuser",
                "not-an-email",
                "StrongPass123!",
                "StrongPass123!",
            ),
            (
                "numeric_password",
                "testuser",
                "test@test.com",
                "12345678",
                "12345678",
            ),
            (
                "common_password",
                "testuser",
                "test@test.com",
                "password123",
                "password123",
            ),
        ]
    )
    def test_register_invalid_input(
        self, name, username, email, password1, password2
    ):
        """Invalid inputs should not create a user"""
        self.client.post(
            self.url,
            {
                "username": username,
                "email": email,
                "password1": password1,
                "password2": password2,
            },
        )
        self.assertFalse(User.objects.filter(username=username).exists())

    # ── Parametrized: valid registration inputs

    @parameterized.expand(
        [
            ("normal_user", "naz", "naz@test.com", "StrongPass123!"),
            (
                "long_username",
                "verylongusername123",
                "a@b.com",
                "StrongPass123!",
            ),
            ("numbers_in_name", "user123", "user@test.com", "StrongPass123!"),
        ]
    )
    def test_register_valid_inputs(self, name, username, email, password):
        """Valid inputs should successfully create a user"""
        self.client.post(
            self.url,
            {
                "username": username,
                "email": email,
                "password1": password,
                "password2": password,
            },
        )
        self.assertTrue(User.objects.filter(username=username).exists())


class LoginViewTests(TestCase):
    """Tests for user login"""

    def setUp(self):
        self.client = Client()
        self.url = reverse("login")
        self.user = User.objects.create_user(
            username="testuser", password="StrongPass123!"
        )

    # ── Happy paths

    def test_login_page_loads(self):
        """Login page returns 200"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_login_valid_credentials(self):
        """Valid credentials log in and redirect to profile"""
        response = self.client.post(
            self.url,
            {
                "username": "testuser",
                "password": "StrongPass123!",
            },
        )
        self.assertRedirects(response, reverse("profile"))

    def test_login_redirects_if_already_logged_in(self):
        """Already logged-in user is redirected to profile"""
        self.client.login(username="testuser", password="StrongPass123!")
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("profile"))

    def test_login_respects_next_param(self):
        """Login redirects to ?next= URL after success"""
        response = self.client.post(
            self.url + "?next=/accounts/profile/",
            {"username": "testuser", "password": "StrongPass123!"},
        )
        self.assertRedirects(response, "/accounts/profile/")

    # ── Sad paths

    def test_login_empty_fields(self):
        """Empty form stays on login page"""
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 200)

    # ── Parametrized: invalid login attempts

    @parameterized.expand(
        [
            ("wrong_password", "testuser", "WrongPassword!"),
            ("wrong_username", "nobody", "StrongPass123!"),
            ("both_wrong", "nobody", "WrongPassword!"),
            ("empty_password", "testuser", ""),
            ("empty_username", "", "StrongPass123!"),
            ("sql_injection", "' OR '1'='1", "anything"),
            ("case_sensitive_user", "TESTUSER", "StrongPass123!"),
        ]
    )
    def test_login_invalid_attempts(self, name, username, password):
        """Invalid login attempts should stay on login page"""
        response = self.client.post(
            self.url,
            {
                "username": username,
                "password": password,
            },
        )
        self.assertEqual(response.status_code, 200)


class LogoutViewTests(TestCase):
    """Tests for logout"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="StrongPass123!"
        )

    def test_logout_redirects_to_home(self):
        """Logout redirects to landing page"""
        self.client.login(username="testuser", password="StrongPass123!")
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("index"))

    def test_logout_clears_session(self):
        """After logout, profile page is inaccessible"""
        self.client.login(username="testuser", password="StrongPass123!")
        self.client.post(reverse("logout"))
        response = self.client.get(reverse("profile"))
        self.assertRedirects(
            response, "/accounts/login/?next=/accounts/profile/"
        )


class ProfileViewTests(TestCase):
    """Tests for user profile"""

    def setUp(self):
        self.client = Client()
        self.url = reverse("profile")
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPass123!",
        )
        UserProfile.objects.create(user=self.user)

    # ── Happy paths

    def test_profile_loads_for_logged_in_user(self):
        """Profile page returns 200 for authenticated user"""
        self.client.login(username="testuser", password="StrongPass123!")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profile.html")

    def test_profile_shows_username(self):
        """Profile page displays the logged-in username"""
        self.client.login(username="testuser", password="StrongPass123!")
        response = self.client.get(self.url)
        self.assertContains(response, "testuser")

    # ── Sad paths

    def test_profile_redirects_unauthenticated(self):
        """Unauthenticated user is redirected to login"""
        response = self.client.get(self.url)
        self.assertRedirects(
            response, "/accounts/login/?next=/accounts/profile/"
        )


class GuestViewTests(TestCase):
    """Tests for guest mode"""

    def setUp(self):
        self.client = Client()
        self.url = reverse("login_as_guest")

    def test_guest_mode_redirects_to_home(self):
        """Guest mode POST redirects to landing page"""
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("index"))

    def test_guest_mode_sets_session_flag(self):
        """Guest mode sets is_guest session flag"""
        self.client.post(self.url)
        self.assertTrue(self.client.session.get("is_guest"))


class UserProfileModelTests(TestCase):
    """Tests for UserProfile model"""

    # ── Parametrized: initials generation

    @parameterized.expand(
        [
            ("username_only", "nazanin", "", "", "NA"),
            ("full_name", "naz", "Nazanin", "Siavash", "NS"),
            ("single_name", "naz", "Nazanin", "", "NA"),
            ("short_username", "nz", "", "", "NZ"),
            ("numbers_username", "user123", "", "", "US"),
        ]
    )
    def test_get_initials(self, name, username, first, last, expected):
        """get_initials returns correct value based on name fields"""
        user = User.objects.create_user(
            username=username,
            first_name=first,
            last_name=last,
            password="Pass12345!",
        )
        profile = UserProfile.objects.create(user=user)
        self.assertEqual(profile.get_initials(), expected)

    def test_profile_str(self):
        """UserProfile __str__ returns username's profile"""
        user = User.objects.create_user(username="naz", password="Pass12345!")
        profile = UserProfile.objects.create(user=user)
        self.assertEqual(str(profile), "naz's profile")

    def test_profile_deleted_with_user(self):
        """Deleting a user also deletes their profile (CASCADE)"""
        user = User.objects.create_user(username="naz", password="Pass12345!")
        UserProfile.objects.create(user=user)
        user.delete()
        self.assertFalse(
            UserProfile.objects.filter(user__username="naz").exists()
        )
