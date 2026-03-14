from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from .models import Card

# Create model cards for testing purposes
class CardModelTest(TestCase):
    def setUp(self):
        self.card = Card.objects.create(
            name="Charizard VMAX",
            set_name="Sword & Shield",
            grade=Decimal("9.5"),
        )

    # Test proper string rep
    def test_card_str(self):
        self.assertIn("Charizard VMAX", str(self.card))

    # Test initial grading
    def test_card_default_grade_is_null(self):
        card = Card.objects.create(name="No Grade Card")
        self.assertIsNone(card.grade)

    # Test initial naming
    def test_card_default_set_name(self):
        card = Card.objects.create(name="No Set Card")
        self.assertEqual(card.set_name, "Unknown Set")

    def test_scanned_at_auto_set(self):
        self.assertIsNotNone(self.card.scanned_at)


class HistoryViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        Card.objects.create(name="Pikachu", set_name="Promo", grade=Decimal("10.0"))
        Card.objects.create(name="Mewtwo EX", set_name="Base Set", grade=Decimal("7.0"))

    def test_history_page_loads(self):
        response = self.client.get(reverse('history'))
        self.assertEqual(response.status_code, 200)

    def test_history_uses_correct_template(self):
        response = self.client.get(reverse('history'))
        self.assertTemplateUsed(response, 'history.html')

    def test_history_shows_cards(self):
        response = self.client.get(reverse('history'))
        self.assertContains(response, "Pikachu")
        self.assertContains(response, "Mewtwo EX")

    def test_history_ordered_by_most_recent(self):
        response = self.client.get(reverse('history'))
        cards = list(response.context['cards'])
        self.assertGreaterEqual(cards[0].scanned_at, cards[-1].scanned_at)


class IndexViewTest(TestCase):
    def test_index_page_loads(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_index_uses_correct_template(self):
        response = self.client.get(reverse('index'))
        self.assertTemplateUsed(response, 'index.html')