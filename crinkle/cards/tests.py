import os
import tempfile

from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from parameterized import parameterized

from .models import GradeReport, Card, CardCollection
from .forms import CollectionSettingsForm


# Create your tests here.
class CollectionTestCase(TestCase):
    def set_up_user(self):
        """create and login a test user"""
        username = "username"
        password = "p1234567890"
        self.user = User.objects.create_user(username=username, password=password)
        self.client.login(username=username, password=password)

    def set_up_collection(self):
        """create a collection for the purpose of setup"""
        self.collection = CardCollection.objects.create(user=self.user)
        self.collection.save()

        self.assertIsNotNone(self.collection.__str__())

    def set_up_add_card(self):
        """simulates saving a card to the collection"""
        notes = GradeReport.objects.create(grade="Grade")
        card = Card.objects.create(
            user=self.user,
            name="Card",
            grading_notes=notes,
            picture_path="/",
            user_notes="",
        )
        card.name += f"-{card.pk}"  # add card primary key as differentiator
        card.save()
        self.cards = Card.objects.all()
        self.collection.cards.add(card)

        self.assertIsNotNone(notes.__str__())
        self.assertIsNotNone(card.__str__())

    def test_retrieve_no_login(self):
        """Test retrieval when not logged in"""
        response = self.client.get(reverse("cards:collection"))
        # No response should be given, not authenticated should recieved 403 response
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["detail"].code, "not_authenticated")

    def test_retrieve_no_cards(self):
        """With no cards or collection the user should retrieve an empty collection"""
        self.set_up_user()
        response = self.client.get(reverse("cards:collection"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["cards"], [])

        # check the cards returned, given seperately for ordering
        self.assertEqual(response.data["cards"], [])

    def test_retrieve_no_cards_belonging_to_user(self):
        """If there are cards but they don't belong to the user, they shouldn't be shown"""
        user = User.objects.create(password="test_pass", username="inactive user")
        notes = GradeReport.objects.create(grade="Grade")
        card = Card.objects.create(
            user=user,
            name="Card",
            grading_notes=notes,
            picture_path="/",
            user_notes="",
        )
        card.save()  # save card not belonging to active user

        self.set_up_user()
        response = self.client.get(reverse("cards:collection"))

        self.assertEqual(response.status_code, 200)

        # check that no cards were returned as the only card belongs to another user
        self.assertEqual(response.data["cards"], [])

    def test_retrieve_collection_with_cards(self):
        """The standard case a collection is present with some cards in it"""
        self.set_up_user()
        self.set_up_collection()
        self.set_up_add_card()
        self.set_up_add_card()
        self.set_up_add_card()

        # Show check that card and collection is created before proceeding
        self.assertIsNotNone(self.collection.__str__())

        response = self.client.get(reverse("cards:collection"))

        self.assertEqual(response.status_code, 200)

        # Check that all cards are present
        for card in response.data["cards"]:
            self.assertEqual(card["name"], f"Card-{card['id']}")
            self.assertEqual(card["user"], self.user.pk)

    @parameterized.expand([order[0] for order in CardCollection.SORT_CHOICES])
    def test_retrieve_cards_ordered_name(self, sort_order):
        """test that cards can be sorted in varying orderings"""
        self.set_up_user()
        self.set_up_collection()
        self.set_up_add_card()
        self.set_up_add_card()

        self.collection.sort_order = sort_order
        self.collection.save()  # save sort order for testing

        # make a request where the specified order is name
        response = self.client.get(
            reverse("cards:collection"),
        )

        self.assertEqual(response.status_code, 200)

        # order the cards by the intended order
        ordered_cards = self.collection.ordered_collection()

        # The ordered cards should be in the same order as the collection's cards
        for card in range(len(response.data["cards"])):
            # The cards of the responses should be in the same ordering
            response_card = response.data["cards"][card]["id"]
            ordered_card = ordered_cards[card].id
            self.assertEqual(response_card, ordered_card)

    def test_access_settings_not_logged_in(self):
        """No settings given if not logged in"""
        response = self.client.get(reverse("cards:collection_settings"))

        self.assertEqual(response.status_code, 403)

    def test_access_settings(self):
        """when accessing settings of collection, it should return a form"""
        self.set_up_user()

        response = self.client.get(reverse("cards:collection_settings"))

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data["form"])

    @parameterized.expand(
        [
            ("name", 100, 100),
            ("grading_notes", -100, 0),
            ("date_scanned", 5, 5),
            ("date_scanned", 50, 50),
        ]
    )
    def test_modify_settings(
        self, sort_order, value_threshold, expected_value_threshold
    ):
        self.set_up_user()
        self.set_up_collection()

        form = CollectionSettingsForm(
            data={
                "sort_order": sort_order,
                "value_threshold": value_threshold,
            },
            instance=self.collection,
        )

        if value_threshold < 0:
            self.assertFalse(form.is_valid())
        else:
            self.assertTrue(form.is_valid())
            form.save()
            self.assertEqual(self.collection.value_threshold, expected_value_threshold)
            self.assertEqual(self.collection.sort_order, sort_order)


class CardTestCase(TestCase):
    def set_up_user(self):
        """create and login a test user"""
        username = "username"
        password = "p1234567890"
        self.user = User.objects.create_user(username=username, password=password)
        self.client.login(username=username, password=password)

    def set_up_add_card(self):
        """simulates saving a card to the collection"""
        notes = GradeReport.objects.create(grade="Grade")
        card = Card.objects.create(
            user=self.user,
            name="Card",
            grading_notes=notes,
            picture_path="/",
            user_notes="",
        )
        card.name += f"-{card.pk}"  # add card primary key as differentiator
        card.save()
        self.cards = Card.objects.all()

    def test_retrieve_no_login(self):
        """The user must be logged in to view cards"""
        response = self.client.get(reverse("cards:view_card", args=[1]))
        # No response should be given, not authenticated should recieved 403 response
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["detail"].code, "not_authenticated")

    def test_retrieve_no_cards(self):
        """If there is no card to retrieve nothing should be found"""
        self.set_up_user()
        response = self.client.get(reverse("cards:view_card", args=[1]))
        # No response to recieve give 404
        self.assertEqual(response.status_code, 404)

    def test_retrieve(self):
        """With the user logged in and cards existing, the user should be able to retrieve a card"""
        self.set_up_user()
        self.set_up_add_card()
        response = self.client.get(
            reverse("cards:view_card", args=[self.cards.first().pk])
        )

        # a card should be retrived status returned will be 200
        self.assertEqual(response.status_code, 200)

        # on success the name of the returned card will be the first and only card
        # as only one was added
        self.assertEqual(response.data["name"], self.cards.first().name)

    def test_save_notes(self):
        """The user should be able to write and save notes to cards"""
        self.set_up_user()
        self.set_up_add_card()
        self.assertEqual(self.cards.first().user_notes, "")  # no notes yet

        test_note = "This is a test note"
        response = self.client.post(
            reverse("cards:save_card", args=[self.cards.first().pk]),
            data={"user_notes": test_note},
        )

        # a 200 status code should be recieved, and data of the updated card will be displayed
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["user_notes"], test_note)

    def test_mock_view_report(self):
        """test mocking function, not much effort put into this as it is simply a mock function standing
        in for later implementations
        """

        self.set_up_user()
        response = self.client.get(reverse("cards:scan_report"))

        # ok it was created
        self.assertEqual(response.status_code, 200)

    def test_mock_save_report(self):
        """save_report should redirect after a logged-in user saves"""
        self.set_up_user()

        response = self.client.get(reverse("cards:save_report"), follow=True)

        self.assertEqual(response.status_code, 200)


TEST_CAPTURED_IMAGE = (
    "data:image/png;base64,"
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO2R0xQAAAAASUVORK5CYII="
)


class ScannedImageSaveTests(TestCase):
    def setUp(self):
        self.temp_media = tempfile.TemporaryDirectory()
        self.override = override_settings(MEDIA_ROOT=self.temp_media.name)
        self.override.enable()
        self.client = self.client_class()
        self.user = User.objects.create_user(username="collector", password="p1234567890")

    def tearDown(self):
        self.override.disable()
        self.temp_media.cleanup()

    def test_guest_can_view_grade_report_with_captured_image(self):
        response = self.client.post(
            reverse("cards:scan_report"),
            data={"captured_image": TEST_CAPTURED_IMAGE},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Guest")
        self.assertContains(response, "Create an account to save this scan to your collection.")
        self.assertEqual(self.client.session.get("captured_scan_image"), TEST_CAPTURED_IMAGE)

    def test_guest_cannot_save_scan_to_collection(self):
        session = self.client.session
        session["captured_scan_image"] = TEST_CAPTURED_IMAGE
        session.save()

        response = self.client.get(reverse("cards:save_report"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])
        self.assertEqual(Card.objects.count(), 0)

    def test_authenticated_user_save_report_persists_scan_image(self):
        self.client.force_login(self.user)
        session = self.client.session
        session["captured_scan_image"] = TEST_CAPTURED_IMAGE
        session.save()

        response = self.client.get(reverse("cards:save_report"), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Card.objects.count(), 1)
        saved_card = Card.objects.get()
        self.assertTrue(saved_card.picture_path.startswith("/media/scans/"))
        self.assertEqual(saved_card.user, self.user)

        relative_path = saved_card.picture_path.replace("/media/", "", 1)
        self.assertTrue(os.path.exists(os.path.join(self.temp_media.name, relative_path)))
        self.assertTrue(CardCollection.objects.filter(user=self.user, cards=saved_card).exists())
from unittest.mock import patch, MagicMock


class AIGradingModuleTests(TestCase):
    """Unit tests for the ai_grading module"""

    def test_fallback_grade_returned_on_invalid_image(self):
        """If image has no base64 data, fallback grade is returned"""
        from cards.ai_grading import analyze_card_with_gemini
        result = analyze_card_with_gemini("not-a-valid-image")
        self.assertEqual(result["psa_grade"], 7)
        self.assertEqual(result["card_name"], "Unknown Card")

    def test_fallback_grade_has_all_fields(self):
        """Fallback grade should always have all required fields"""
        from cards.ai_grading import _fallback_grade
        result = _fallback_grade()
        self.assertIn("psa_grade", result)
        self.assertIn("card_name", result)
        self.assertIn("corners", result)
        self.assertIn("edges", result)
        self.assertIn("centering", result)
        self.assertIn("surface", result)

    @patch("cards.ai_grading.urllib.request.urlopen")
    def test_successful_api_response_parsed_correctly(self, mock_urlopen):
        """A valid API response should be parsed into a grade dict"""
        from cards.ai_grading import analyze_card_with_gemini
        mock_response = MagicMock()
        mock_response.read.return_value = b'''{
            "choices": [{
                "message": {
                    "content": "{\\"psa_grade\\": 8, \\"card_name\\": \\"Charizard\\", \\"corners\\": \\"Sharp.\\", \\"edges\\": \\"Clean.\\", \\"centering\\": \\"Centered.\\", \\"surface\\": \\"No scratches.\\"}"
                }
            }]
        }'''
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        image = "data:image/jpeg;base64,/9j/4AAQSkZJRgAB"
        result = analyze_card_with_gemini(image)
        self.assertEqual(result["psa_grade"], 8)
        self.assertEqual(result["card_name"], "Charizard")

    @patch("cards.ai_grading.urllib.request.urlopen")
    def test_api_error_returns_fallback(self, mock_urlopen):
        """If API call throws exception, fallback grade is returned"""
        from cards.ai_grading import analyze_card_with_gemini
        mock_urlopen.side_effect = Exception("Network error")
        image = "data:image/jpeg;base64,/9j/4AAQSkZJRgAB"
        result = analyze_card_with_gemini(image)
        self.assertEqual(result["psa_grade"], 7)
        self.assertEqual(result["card_name"], "Unknown Card")


class ScanReportAITests(TestCase):
    """Tests for scan_report_view with AI grading"""

    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="p1234567890")

    @patch("cards.views.analyze_card_with_gemini")
    def test_post_triggers_ai_grading(self, mock_ai):
        """Posting a captured image should trigger AI grading"""
        mock_ai.return_value = {
            "psa_grade": 9,
            "card_name": "Pikachu",
            "corners": "Sharp corners.",
            "edges": "Clean edges.",
            "centering": "Well centered.",
            "surface": "No scratches.",
        }
        response = self.client.post(
            reverse("cards:scan_report"),
            data={"captured_image": TEST_CAPTURED_IMAGE},
        )
        self.assertEqual(response.status_code, 200)
        mock_ai.assert_called_once()

    @patch("cards.views.analyze_card_with_gemini")
    def test_grade_result_shown_in_response(self, mock_ai):
        """Grade result from AI should appear in the rendered page"""
        mock_ai.return_value = {
            "psa_grade": 9,
            "card_name": "Pikachu",
            "corners": "Sharp corners.",
            "edges": "Clean edges.",
            "centering": "Well centered.",
            "surface": "No scratches.",
        }
        response = self.client.post(
            reverse("cards:scan_report"),
            data={"captured_image": TEST_CAPTURED_IMAGE},
        )
        self.assertContains(response, "Pikachu")
        self.assertContains(response, "Sharp corners.")

    @patch("cards.views.analyze_card_with_gemini")
    def test_guest_sees_grade_result(self, mock_ai):
        """Guest users should also see the AI grade result"""
        mock_ai.return_value = {
            "psa_grade": 6,
            "card_name": "Mewtwo",
            "corners": "Slight wear.",
            "edges": "Minor chips.",
            "centering": "Off center.",
            "surface": "Light scratches.",
        }
        response = self.client.post(
            reverse("cards:scan_report"),
            data={"captured_image": TEST_CAPTURED_IMAGE},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mewtwo")

    @patch("cards.views.analyze_card_with_gemini")
    def test_grade_stored_in_session(self, mock_ai):
        """Grade result should be stored in the session after POST"""
        mock_ai.return_value = {
            "psa_grade": 8,
            "card_name": "Bulbasaur",
            "corners": "Good corners.",
            "edges": "Good edges.",
            "centering": "Centered.",
            "surface": "Clean.",
        }
        self.client.post(
            reverse("cards:scan_report"),
            data={"captured_image": TEST_CAPTURED_IMAGE},
        )
        session_grade = self.client.session.get("card_grade_result")
        self.assertIsNotNone(session_grade)
        self.assertEqual(session_grade["psa_grade"], 8)
        self.assertEqual(session_grade["card_name"], "Bulbasaur")

class SaveReportVmMediaTests(TestCase):
    def setUp(self):
        self.temp_media = tempfile.TemporaryDirectory()
        self.override = override_settings(
            MEDIA_ROOT=self.temp_media.name,
            MEDIA_URL='/media/',
        )
        self.override.enable()
        self.user = User.objects.create_user(username='vmuser', password='StrongPass123!')
        self.client.login(username='vmuser', password='StrongPass123!')

    def tearDown(self):
        self.override.disable()
        self.temp_media.cleanup()

    def _store_captured_scan(self):
        session = self.client.session
        session['captured_scan_image'] = TEST_CAPTURED_IMAGE
        session.save()

    def test_save_report_writes_scan_under_media_root_and_links_card_to_user_collection(self):
        self._store_captured_scan()

        response = self.client.get(reverse('cards:save_report'), follow=True)

        self.assertEqual(response.status_code, 200)
        saved_card = Card.objects.get(user=self.user)
        self.assertTrue(saved_card.picture_path.startswith('/media/scans/'))

        relative_path = saved_card.picture_path.replace('/media/', '', 1)
        saved_file = os.path.join(self.temp_media.name, relative_path)
        self.assertTrue(os.path.exists(saved_file))
        self.assertTrue(CardCollection.objects.filter(user=self.user, cards=saved_card).exists())

    def test_collection_page_renders_saved_scan_image_for_logged_in_user(self):
        self._store_captured_scan()
        self.client.get(reverse('cards:save_report'), follow=True)

        response = self.client.get(reverse('cards:collection'))

        self.assertEqual(response.status_code, 200)
        saved_card = Card.objects.get(user=self.user)
        self.assertContains(response, saved_card.picture_path)
        self.assertContains(response, saved_card.name)
