import requests
from django.core.management.base import BaseCommand
from tracking.models import CardPricing
from datetime import datetime
import os

API_KEY = os.environ.get('POKEMON_PRICE_API_KEY', '')
BASE_URL = 'https://www.pokemonpricetracker.com/api/v2/cards'

CARDS = [
    'Charizard EX',
    'Pikachu',
    'Mewtwo',
    'Blastoise',
    'Venusaur',
    'Alakazam',
    'Lugia',
    'Umbreon',
    'Espeon',
    'Rayquaza',
    'Gardevoir',
    'Gyarados',
    'Gengar',
    'Dragonite',
    'Machamp',
    'Raichu',
    'Articuno',
    'Zapdos',
    'Moltres',
    'Mew',
    'Jolteon',
    'Vaporeon',
    'Flareon',
    'Snorlax',
    'Lapras',
    'Arcanine',
    'Ninetales',
    'Scyther',
    'Pinsir',
    'Magmar',
    'Electabuzz',
    'Hitmonchan',
    'Kangaskhan',
    'Clefable',
    'Wigglytuff',
    'Nidoking',
    'Nidoqueen',
    'Slowbro',
    'Hypno',
    'Exeggutor',
    'Starmie',
    'Poliwrath',
    'Victreebel',
    'Vileplume',
    'Golem',
    'Magneton',
    'Haunter',
    'Kadabra',
    'Wartortle',
    'Charmeleon',
]

CONDITION_MAP = {
    'Near Mint': 'near_mint',
    'Lightly Played': 'lightly_played',
    'Moderately Played': 'moderately_played',
    'Heavily Played': 'heavily_played',
    'Damaged': 'damaged',
}


class Command(BaseCommand):  # pragma: no cover
    help = 'Load real pricing data from PokemonPriceTracker API'

    def handle(self, *args, **options):
        if not API_KEY:
            self.stdout.write(self.style.ERROR('POKEMON_PRICE_API_KEY not set'))
            return

        CardPricing.objects.all().delete()
        loaded = 0

        for card_name in CARDS:
            self.stdout.write(f'Fetching {card_name}...')
            try:
                response = requests.get(
                    BASE_URL,
                    headers={'Authorization': f'Bearer {API_KEY}'},
                    params={
                        'search': card_name,
                        'limit': 1,
                        'includeHistory': 'true',
                        'days': 3,
                    },
                    timeout=10,
                )
                data = response.json()

                if not data.get('data'):
                    self.stdout.write(f'  No results for {card_name}, skipping')
                    continue

                card = data['data'][0]
                card_set = card.get('setName', '')
                tcg_player_id = card.get('tcgPlayerId', '')
                image_url = card.get('imageCdnUrl200', '')
                history = card.get('priceHistory', {}).get('conditions', {})

                for condition_label, condition_key in CONDITION_MAP.items():
                    condition_data = history.get(condition_label, {})
                    history_points = condition_data.get('history', [])

                    if not history_points:
                        latest_price = card.get('prices', {}).get('market')
                        if latest_price:
                            CardPricing.objects.create(
                                card_name=card.get('name', card_name),
                                card_set=card_set,
                                tcg_player_id=tcg_player_id,
                                image_url=image_url,
                                grade_tier=condition_key,
                                price=round(latest_price, 2),
                            )
                            loaded += 1
                        continue

                    for point in history_points:
                        date_recorded = datetime.fromisoformat(
                            point['date'].replace('Z', '+00:00')
                        ).date()
                        CardPricing.objects.create(
                            card_name=card.get('name', card_name),
                            card_set=card_set,
                            tcg_player_id=tcg_player_id,
                            image_url=image_url,
                            grade_tier=condition_key,
                            price=round(point['market'], 2),
                            date_recorded=date_recorded,
                        )
                        loaded += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  Error fetching {card_name}: {e}'))
                continue

        self.stdout.write(self.style.SUCCESS(f'Loaded {loaded} pricing records'))