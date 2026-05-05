from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import TrackedCard, ValueSnapshot, CardPricing


class TrackedCardModelTest(TestCase):
    def setUp(self):
        self.card = TrackedCard.objects.create(
            card_name="Charizard",
            card_set="Base Set",
            card_year=1999,
            grade_tier="psa_9",
            status="watching",
            notes="Test card",
        )

    def test_card_creation(self):
        self.assertEqual(self.card.card_name, "Charizard")
        self.assertEqual(self.card.card_set, "Base Set")

    def test_card_str(self):
        self.assertIn("Charizard", str(self.card))
        self.assertIn("PSA 9", str(self.card))

    def test_default_status(self):
        card = TrackedCard.objects.create(card_name="Pikachu")
        self.assertEqual(card.status, "watching")
        self.assertEqual(card.grade_tier, "ungraded")

    def test_sold_price_nullable(self):
        self.assertIsNone(self.card.sold_price)

    def test_last_price_nullable(self):
        self.assertIsNone(self.card.last_price)

    def test_price_trend_default(self):
        self.assertEqual(self.card.price_trend, "")


class ValueSnapshotModelTest(TestCase):
    def test_snapshot_creation(self):
        snapshot = ValueSnapshot.objects.create(total_value=500.00)
        self.assertEqual(float(snapshot.total_value), 500.00)

    def test_snapshot_str(self):
        snapshot = ValueSnapshot.objects.create(total_value=250.00)
        self.assertIn("$250", str(snapshot))


class CardPricingModelTest(TestCase):
    def test_pricing_creation(self):
        pricing = CardPricing.objects.create(
            card_name="Charizard",
            card_set="Base Set",
            grade_tier="near_mint",
            price=5000.00,
        )
        self.assertEqual(pricing.card_name, "Charizard")
        self.assertEqual(float(pricing.price), 5000.00)

    def test_pricing_str(self):
        pricing = CardPricing.objects.create(
            card_name="Charizard",
            card_set="Base Set",
            grade_tier="near_mint",
            price=5000.00,
        )
        self.assertIn("Charizard", str(pricing))
        self.assertIn("5000", str(pricing))


class TrackingViewsTest(TestCase):
    def setUp(self):
        self.client = Client()

        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpass123",
        )
        self.client.force_login(self.user)

        self.card = self.create_tracked_card(
            card_name="Mewtwo",
            card_set="Base Set",
            card_year=1999,
            grade_tier="psa_10",
            status="watching",
        )

    def create_tracked_card(self, **kwargs):
        defaults = {"user": self.user}
        defaults.update(kwargs)
        return TrackedCard.objects.create(**defaults)

    def test_list_view_status(self):
        response = self.client.get(reverse("tracking:list"))
        self.assertEqual(response.status_code, 200)

    def test_list_view_shows_card(self):
        response = self.client.get(reverse("tracking:list"))
        self.assertContains(response, "Mewtwo")

    def test_list_view_filter_by_status(self):
        self.create_tracked_card(card_name="Pikachu", status="sold")
        response = self.client.get(reverse("tracking:list") + "?status=sold")
        self.assertContains(response, "Pikachu")
        self.assertNotContains(response, "Mewtwo")

    def test_list_view_filter_all(self):
        self.create_tracked_card(card_name="Pikachu", status="sold")
        response = self.client.get(reverse("tracking:list"))
        self.assertContains(response, "Mewtwo")
        self.assertContains(response, "Pikachu")

    def test_detail_view(self):
        response = self.client.get(
            reverse("tracking:detail", args=[self.card.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mewtwo")

    def test_detail_view_404(self):
        response = self.client.get(reverse("tracking:detail", args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_add_view_get(self):
        response = self.client.get(reverse("tracking:add"))
        self.assertEqual(response.status_code, 200)

    def test_add_view_post(self):
        response = self.client.post(
            reverse("tracking:add"),
            {
                "card_name": "Blastoise",
                "card_set": "Base Set",
                "card_year": 1999,
                "grade_tier": "psa_8",
                "status": "watching",
                "notes": "",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            TrackedCard.objects.filter(
                user=self.user,
                card_name="Blastoise",
            ).exists()
        )

    def test_add_view_invalid(self):
        response = self.client.post(
            reverse("tracking:add"),
            {
                "card_name": "",
                "grade_tier": "psa_8",
                "status": "watching",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(TrackedCard.objects.filter(card_name="").exists())

    def test_edit_view_get(self):
        response = self.client.get(
            reverse("tracking:edit", args=[self.card.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_edit_view_post(self):
        response = self.client.post(
            reverse("tracking:edit", args=[self.card.pk]),
            {
                "card_name": "Mewtwo",
                "card_set": "Base Set",
                "card_year": 1999,
                "grade_tier": "psa_10",
                "status": "watching",
                "notes": "Sent to PSA",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.card.refresh_from_db()
        self.assertEqual(self.card.status, "watching")

    def test_delete_view_get(self):
        response = self.client.get(
            reverse("tracking:delete", args=[self.card.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mewtwo")

    def test_delete_view_post(self):
        response = self.client.post(
            reverse("tracking:delete", args=[self.card.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(TrackedCard.objects.filter(pk=self.card.pk).exists())

    def test_sold_total_in_context(self):
        self.create_tracked_card(
            card_name="Venusaur",
            status="sold",
            sold_price=150.00,
        )
        self.create_tracked_card(
            card_name="Blastoise",
            status="sold",
            sold_price=200.00,
        )
        response = self.client.get(reverse("tracking:list") + "?status=sold")
        self.assertEqual(float(response.context["sold_total"]), 350.00)

    def test_market_search_page(self):
        response = self.client.get(reverse("tracking:market"))
        self.assertEqual(response.status_code, 200)

    def test_market_search_with_query(self):
        CardPricing.objects.create(
            card_name="Charizard",
            card_set="Base Set",
            grade_tier="near_mint",
            price=50.00,
        )
        response = self.client.get(reverse("tracking:market") + "?q=Charizard")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Charizard")

    def test_market_search_no_results(self):
        response = self.client.get(
            reverse("tracking:market") + "?q=nonexistent"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No results")

    def test_card_pricing_page(self):
        CardPricing.objects.create(
            card_name="Charizard",
            card_set="Base Set",
            grade_tier="near_mint",
            price=50.00,
        )
        response = self.client.get(
            reverse("tracking:card_pricing") + "?name=Charizard&set=Base+Set"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Charizard")

    def test_card_pricing_no_name_redirects(self):
        response = self.client.get(reverse("tracking:card_pricing"))
        self.assertEqual(response.status_code, 302)

    def test_card_pricing_shows_tiers(self):
        for tier in [
            "near_mint",
            "lightly_played",
            "moderately_played",
            "heavily_played",
            "damaged",
        ]:
            CardPricing.objects.create(
                card_name="Pikachu",
                card_set="Base Set",
                grade_tier=tier,
                price=100.00,
            )
        response = self.client.get(
            reverse("tracking:card_pricing") + "?name=Pikachu&set=Base+Set"
        )
        self.assertContains(response, "Near Mint")
        self.assertContains(response, "Damaged")

    def test_market_watch_post(self):
        response = self.client.post(
            reverse("tracking:market_watch"),
            {
                "card_name": "Charizard",
                "card_set": "Base Set",
                "grade_tier": "near_mint",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            TrackedCard.objects.filter(
                user=self.user,
                card_name="Charizard",
                status="watching",
            ).exists()
        )

    def test_market_watch_duplicate(self):
        self.create_tracked_card(
            card_name="Charizard",
            card_set="Base Set",
            grade_tier="near_mint",
            status="watching",
        )
        response = self.client.post(
            reverse("tracking:market_watch"),
            {
                "card_name": "Charizard",
                "card_set": "Base Set",
                "grade_tier": "near_mint",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            TrackedCard.objects.filter(
                user=self.user,
                card_name="Charizard",
                card_set="Base Set",
                grade_tier="near_mint",
            ).count(),
            1,
        )

    def test_market_compare_page(self):
        CardPricing.objects.create(
            card_name="Charizard",
            card_set="Base Set",
            grade_tier="near_mint",
            price=100.00,
        )
        CardPricing.objects.create(
            card_name="Pikachu",
            card_set="Base Set",
            grade_tier="near_mint",
            price=50.00,
        )
        response = self.client.get(
            reverse("tracking:market_compare")
            + "?name=Charizard&set=Base+Set&name=Pikachu&set=Base+Set"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Charizard")
        self.assertContains(response, "Pikachu")

    def test_tracking_detail_with_pricing(self):
        CardPricing.objects.create(
            card_name="Mewtwo",
            card_set="Base Set",
            grade_tier="psa_10",
            price=500.00,
            image_url="https://example.com/img.jpg",
        )
        response = self.client.get(
            reverse("tracking:detail", args=[self.card.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mewtwo")


class TrackedCardFormTest(TestCase):
    def test_valid_form(self):
        from .forms import TrackedCardForm

        form = TrackedCardForm(
            data={
                "card_name": "Charizard",
                "card_set": "Base Set",
                "card_year": 1999,
                "grade_tier": "psa_9",
                "status": "watching",
                "notes": "",
            }
        )
        self.assertTrue(form.is_valid())

    def test_invalid_form_no_name(self):
        from .forms import TrackedCardForm

        form = TrackedCardForm(
            data={
                "card_name": "",
                "grade_tier": "psa_9",
                "status": "watching",
            }
        )
        self.assertFalse(form.is_valid())

    def test_form_with_sold_price(self):
        from .forms import TrackedCardForm

        form = TrackedCardForm(
            data={
                "card_name": "Charizard",
                "card_set": "Base Set",
                "card_year": 1999,
                "grade_tier": "psa_10",
                "status": "sold",
                "sold_price": 500.00,
                "notes": "",
            }
        )
        self.assertTrue(form.is_valid())
