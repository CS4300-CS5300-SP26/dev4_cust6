from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from submission.models import Submission
from parameterized import parameterized


class SubmissionStartViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("submission:start")
        self.user = User.objects.create_user(
            username="testuser", password="StrongPass123!"
        )

    def test_start_page_loads(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "submission/start.html")

    def test_start_page_loads_when_logged_in(self):
        self.client.login(username="testuser", password="StrongPass123!")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_start_post_redirects_to_details(self):
        response = self.client.post(
            self.url,
            {
                "card_name": "Charizard Base Set",
                "grading_service": "PSA",
            },
        )
        self.assertRedirects(response, reverse("submission:details"))

    def test_start_post_saves_to_session(self):
        self.client.post(
            self.url,
            {
                "card_name": "Charizard Base Set",
                "grading_service": "PSA",
            },
        )
        self.assertEqual(self.client.session["submission_service"], "PSA")
        self.assertEqual(
            self.client.session["submission_card_name"], "Charizard Base Set"
        )

    @parameterized.expand(
        [
            ("PSA", "PSA"),
            ("BGS", "BGS"),
        ]
    )
    def test_start_post_both_services(self, name, service):
        response = self.client.post(
            self.url,
            {
                "card_name": "Pikachu",
                "grading_service": service,
            },
        )
        self.assertRedirects(response, reverse("submission:details"))
        self.assertEqual(self.client.session["submission_service"], service)


class SubmissionDetailsViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("submission:details")
        self.user = User.objects.create_user(
            username="testuser", password="StrongPass123!"
        )
        self.valid_data = {
            "card_name": "Charizard Base Set",
            "grading_service": "PSA",
            "full_name": "Naz Siavash",
            "address": "123 Main St",
            "city": "Salt Lake City",
            "state": "UT",
            "zip_code": "84101",
        }

    def test_details_page_loads(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "submission/details.html")

    def test_details_page_prefills_from_session(self):
        session = self.client.session
        session["submission_service"] = "BGS"
        session["submission_card_name"] = "Pikachu"
        session.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pikachu")

    def test_valid_submission_creates_record(self):
        self.client.post(self.url, self.valid_data)
        self.assertTrue(
            Submission.objects.filter(card_name="Charizard Base Set").exists()
        )

    def test_valid_submission_redirects_to_checkout(self):
        response = self.client.post(self.url, self.valid_data)
        submission = Submission.objects.get(card_name="Charizard Base Set")
        self.assertRedirects(
            response,
            reverse("submission:checkout", args=[submission.pk]),
            fetch_redirect_response=False,
        )

    def test_submission_links_to_logged_in_user(self):
        self.client.login(username="testuser", password="StrongPass123!")
        self.client.post(self.url, self.valid_data)
        submission = Submission.objects.get(card_name="Charizard Base Set")
        self.assertEqual(submission.user, self.user)

    def test_submission_no_user_when_guest(self):
        self.client.post(self.url, self.valid_data)
        submission = Submission.objects.get(card_name="Charizard Base Set")
        self.assertIsNone(submission.user)

    def test_invalid_submission_missing_fields(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Submission.objects.exists())

    @parameterized.expand(
        [
            (
                "missing_name",
                "",
                "PSA",
                "Naz",
                "123 Main",
                "SLC",
                "UT",
                "84101",
            ),
            (
                "missing_address",
                "Charizard",
                "PSA",
                "Naz",
                "",
                "SLC",
                "UT",
                "84101",
            ),
        ]
    )
    def test_invalid_inputs(
        self,
        name,
        card_name,
        service,
        full_name,
        address,
        city,
        state,
        zip_code,
    ):
        self.client.post(
            self.url,
            {
                "card_name": card_name,
                "grading_service": service,
                "full_name": full_name,
                "address": address,
                "city": city,
                "state": state,
                "zip_code": zip_code,
            },
        )
        self.assertFalse(
            Submission.objects.filter(
                card_name=card_name, address=address
            ).exists()
        )


class SubmissionConfirmationViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="StrongPass123!"
        )
        self.submission = Submission.objects.create(
            card_name="Charizard Base Set",
            grading_service="PSA",
            full_name="Naz Siavash",
            address="123 Main St",
            city="Salt Lake City",
            state="UT",
            zip_code="84101",
        )
        self.url = reverse(
            "submission:confirmation", args=[self.submission.pk]
        )

    def test_confirmation_page_loads(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "submission/confirmation.html")

    def test_confirmation_shows_card_name(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Charizard Base Set")

    def test_confirmation_shows_service(self):
        response = self.client.get(self.url)
        self.assertContains(response, "PSA")

    def test_confirmation_shows_name(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Naz Siavash")

    def test_confirmation_404_for_invalid_pk(self):
        response = self.client.get(
            reverse("submission:confirmation", args=[9999])
        )
        self.assertEqual(response.status_code, 404)


class SubmissionModelTests(TestCase):
    def test_submission_str(self):
        submission = Submission.objects.create(
            card_name="Pikachu",
            grading_service="BGS",
            full_name="Test User",
            address="123 St",
            city="SLC",
            state="UT",
            zip_code="84101",
        )
        self.assertEqual(str(submission), "Pikachu to BGS")

    def test_submission_default_user_is_none(self):
        submission = Submission.objects.create(
            card_name="Mewtwo",
            grading_service="PSA",
            full_name="Test",
            address="123",
            city="SLC",
            state="UT",
            zip_code="84101",
        )
        self.assertIsNone(submission.user)
