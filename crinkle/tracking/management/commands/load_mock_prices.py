from django.core.management.base import BaseCommand
from tracking.models import CardPricing
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Load mock pricing data for testing'

    def handle(self, *args, **options):
        CardPricing.objects.all().delete()

        cards = [
            ('Charizard', 'Base Set'),
            ('Pikachu', 'Base Set'),
            ('Mewtwo', 'Base Set'),
            ('Blastoise', 'Base Set'),
            ('Venusaur', 'Base Set'),
            ('Alakazam', 'Base Set'),
            ('Lugia', 'Neo Genesis'),
            ('Typhlosion', 'Neo Genesis'),
            ('Umbreon', 'Neo Discovery'),
            ('Espeon', 'Neo Discovery'),
            ('Rayquaza', 'EX Deoxys'),
            ('Gardevoir', 'EX Sandstorm'),
            ('Gold Star Mew', 'Dragon Frontiers'),
            ('Shining Gyarados', 'Neo Revelation'),
            ('Dark Charizard', 'Team Rocket'),
        ]

        tiers = ['ungraded', 'psa_7', 'psa_8', 'psa_9', 'psa_10']

        base_prices = {
            'ungraded': 50,
            'psa_7': 150,
            'psa_8': 300,
            'psa_9': 800,
            'psa_10': 5000,
        }

        for card_name, card_set in cards:
            multiplier = random.uniform(0.5, 3.0)
            for tier in tiers:
                base = base_prices[tier] * multiplier
                for days_ago in range(180, -1, -30):
                    d = date.today() - timedelta(days=days_ago)
                    price = base * random.uniform(0.85, 1.15)
                    CardPricing.objects.create(
                        card_name=card_name,
                        card_set=card_set,
                        grade_tier=tier,
                        price=round(price, 2),
                        date_recorded=d,
                    )

        self.stdout.write(self.style.SUCCESS('Mock pricing data loaded'))