import base64
import tempfile
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from parameterized import parameterized

from .forms import CollectionSettingsForm
from .models import Card, CardCollection, GradeReport, ScannedCard

SAMPLE_IMAGE_DATA_URL = (
    "data:image/png;base64,"
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO7Z3b0AAAAASUVORK5CYII="
)


class CollectionTestCase(TestCase):
    def set_up_user(self):
        username = "username"
        password = "p1234567890"
        self.user = User.objects.create_user(username=username, password=password)
        self.client.login(username=username, password=password)

    def set_up_collection(self):
        self.collection = CardCollection.objects.create(user=self.user)
        self.collection.save()
        self.assertIsNotNone(self.collection.__str__())

    def set_up_add_card(self):
        notes = GradeReport.objects.create(grade="Grade")
        card = Card.objects.create(
            user=self.user,
            name="Card",
            grading_notes=notes,
            picture_path="/",
            user_notes="",
        )
        card.name += f"-{card.pk}"
        card.save()
        self.cards = Card.objects.all()
        self.collection.cards.add(card)

        self.assertIsNotNone(notes.__str__())
        self.assertIsNotNone(card.__str__())

    def test_retrieve_no_login(self):
        response = self.client.get(reverse("cards:collection"))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["detail"].code, "not_authenticated")

    def test_retrieve_no_cards(self):
        self.set_up_user()
        response = self.client.get(reverse("cards:collection"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["cards"], [])

    def test_retrieve_no_cards_belonging_to_user(self):
        user = User.objects.create(password="test_pass", username="inactive user")
        notes = GradeReport.objects.create(grade="Grade")
        card = Card.objects.create(
            user=user,
            name="Card",
            grading_notes=notes,
            picture_path="/",
            user_notes="",
        )
        card.save()

        self.set_up_user()
        response = self.client.get(reverse("cards:collection"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["cards"], [])

    def test_retrieve_collection_with_cards(self):
        self.set_up_user()
        self.set_up_collection()
        self.set_up_add_card()
        self.set_up_add_card()
        self.set_up_add_card()

        response = self.client.get(reverse("cards:collection"))

        self.assertEqual(response.status_code, 200)
        for card in response.data["cards"]:
            self.assertEqual(card["name"], f"Card-{card['id']}")
            self.assertEqual(card["user"], self.user.pk)

    @parameterized.expand([order[0] for order in CardCollection.SORT_CHOICES])
    def test_retrieve_cards_ordered_name(self, sort_order):
        self.set_up_user()
        self.set_up_collection()
        self.set_up_add_card()
        self.set_up_add_card()

        self.collection.sort_order = sort_order
        self.collection.save()

        response = self.client.get(reverse("cards:collection"))

        self.assertEqual(response.status_code, 200)
        ordered_cards = self.collection.ordered_collection()

        for card in range(len(response.data["cards"])):
            response_card = response.data["cards"][card]["id"]
            ordered_card = ordered_cards[card].id
            self.assertEqual(response_card, ordered_card)

    def test_access_settings_not_logged_in(self):
        response = self.client.get(reverse("cards:collection_settings"))
        self.assertEqual(response.status_code, 403)

    def test_access_settings(self):
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
    def test_modify_settings(self, sort_order, value_threshold, expected_value_threshold):
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
        username = "username"
        password = "p1234567890"
        self.user = User.objects.create_user(username=username, password=password)
        self.client.login(username=username, password=password)

    def set_up_add_card(self):
        notes = GradeReport.objects.create(grade="Grade")
        card = Card.objects.create(
            user=self.user,
            name="Card",
            grading_notes=notes,
            picture_path="/",
            user_notes="",
        )
        card.name += f"-{card.pk}"
        card.save()
        self.cards = Card.objects.all()

    def test_retrieve_no_login(self):
        response = self.client.get(reverse("cards:view_card", args=[1]))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["detail"].code, "not_authenticated")

    def test_retrieve_no_cards(self):
        self.set_up_user()
        response = self.client.get(reverse("cards:view_card", args=[1]))
        self.assertEqual(response.status_code, 404)

    def test_retrieve(self):
        self.set_up_user()
        self.set_up_add_card()
        response = self.client.get(reverse("cards:view_card", args=[self.cards.first().pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], self.cards.first().name)

    def test_save_notes(self):
        self.set_up_user()
        self.set_up_add_card()
        self.assertEqual(self.cards.first().user_notes, "")

        test_note = "This is a test note"
        response = self.client.post(
            reverse("cards:save_card", args=[self.cards.first().pk]),
            data={"user_notes": test_note},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["user_notes"], test_note)

    def test_delete_card(self):
        self.set_up_user()
        collection = CardCollection.objects.create(user=self.user)
        self.set_up_add_card()
        card = self.cards.first()
        collection.cards.add(card)

        response = self.client.post(reverse("cards:delete_card", args=[card.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Card.objects.filter(pk=card.pk).exists())
        self.assertEqual(collection.cards.count(), 0)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ScanAndStorageTests(TestCase):
    def setUp(self):
        self.media_root = Path(settings.MEDIA_ROOT)

    def login(self):
        self.user = User.objects.create_user(username="scanner", password="safe-pass-123")
        self.client.login(username="scanner", password="safe-pass-123")

    def test_scan_report_stores_photo_and_grade_for_guest(self):
        response = self.client.post(
            reverse("cards:scan_report"),
            data={"captured_image": SAMPLE_IMAGE_DATA_URL},
        )

        self.assertEqual(response.status_code, 200)
        scan = ScannedCard.objects.get()
        self.assertContains(response, scan.grade)
        self.assertContains(response, "Guests can receive a grade")
        self.assertTrue(scan.picture_path.startswith("/media/card_photos/"))

        stored_file = self.media_root / scan.picture_path.removeprefix("/media/")
        self.assertTrue(stored_file.exists())

    def test_guest_cannot_save_scanned_card(self):
        self.client.post(reverse("login_as_guest"))
        scan_response = self.client.post(
            reverse("cards:scan_report"),
            data={"captured_image": SAMPLE_IMAGE_DATA_URL},
        )
        scan = ScannedCard.objects.get()
        self.assertEqual(scan_response.status_code, 200)

        save_response = self.client.post(
            reverse("cards:save_report"),
            data={"scan_id": scan.pk},
        )

        self.assertEqual(save_response.status_code, 403)
        self.assertEqual(Card.objects.count(), 0)
        self.assertContains(save_response, "must log in to save cards", status_code=403)

    def test_authenticated_user_can_save_scanned_card_to_collection(self):
        self.login()
        scan_response = self.client.post(
            reverse("cards:scan_report"),
            data={"captured_image": SAMPLE_IMAGE_DATA_URL},
        )
        self.assertEqual(scan_response.status_code, 200)
        scan = ScannedCard.objects.get()

        save_response = self.client.post(
            reverse("cards:save_report"),
            data={"scan_id": scan.pk},
        )

        self.assertEqual(save_response.status_code, 302)
        saved_card = Card.objects.get()
        self.assertEqual(saved_card.user, self.user)
        self.assertEqual(saved_card.picture_path, scan.picture_path)
        self.assertEqual(saved_card.grading_notes.grade, scan.grade)
        self.assertEqual(CardCollection.objects.get(user=self.user).cards.count(), 1)

    def test_scan_page_mentions_guest_can_grade_but_save_requires_login(self):
        response = self.client.get(reverse("scan"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Guests can grade cards, but saving requires logging in")
