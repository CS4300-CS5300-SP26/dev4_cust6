import unittest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
from cards.models import Card, GradeReport


# Create model cards for testing purposes
class CardModelTest(TestCase):
    def setUp(self):
        self.card = Card.objects.create(
            name="Charizard VMAX",
            set_name="Sword & Shield",
            grade=Decimal("9.5"),
        )

    # Test proper string rep
    @unittest.skip("This model is no longer in use.")
    def test_card_str(self):
        self.assertIn("Charizard VMAX", str(self.card))

    # Test initial grading
    @unittest.skip("This model is no longer in use.")
    def test_card_default_grade_is_null(self):
        card = Card.objects.create(name="No Grade Card")
        self.assertIsNone(card.grade)

    # Test initial naming
    @unittest.skip("This model is no longer in use.")
    def test_card_default_set_name(self):
        card = Card.objects.create(name="No Set Card")
        self.assertEqual(card.set_name, "Unknown Set")

    @unittest.skip("This model is no longer in use.")
    def test_date_scanned_auto_set(self):
        self.assertIsNotNone(self.card.date_scanned)


class HistoryViewTest(TestCase):
    def set_up_user(self):
        """create and login a test user"""
        username = "username"
        password = "p1234567890"
        self.user = User.objects.create_user(
            username=username, password=password
        )
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
        card.grading_notes.grade = "grade-{card.pk}"
        card.name += f"-{card.pk}"  # add card primary key as differentiator
        card.save()

        self.assertIsNotNone(notes.__str__())
        self.assertIsNotNone(card.__str__())

    def set_up(self):
        self.client = Client()
        self.set_up_user()

        self.set_up_add_card()
        self.set_up_add_card()

    def test_history_page_loads(self):
        self.set_up()
        response = self.client.get(reverse("history"))
        self.assertEqual(response.status_code, 200)

    def test_history_uses_correct_template(self):
        self.set_up()
        response = self.client.get(reverse("history"))
        self.assertTemplateUsed(response, "history.html")

    def test_history_shows_cards(self):
        self.set_up()
        response = self.client.get(reverse("history"))
        self.assertContains(response, "Card-1")
        self.assertContains(response, "Card-2")

    def test_history_ordered_by_most_recent(self):
        self.set_up()
        response = self.client.get(reverse("history"))
        cards = response.data["cards"]
        self.assertGreaterEqual(
            cards[0]["date_scanned"], cards[-1]["date_scanned"]
        )


class IndexViewTest(TestCase):
    def test_index_page_loads(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

    def test_index_uses_correct_template(self):
        response = self.client.get(reverse("index"))
        self.assertTemplateUsed(response, "index.html")
