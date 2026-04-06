from django.db import models
from django.conf import settings


class TrackedCard(models.Model):
    # Dropdown choices for card status
    STATUS_CHOICES = [
        ('watching', 'Watching'),
        ('submitted', 'Submitted for Grading'),
        ('graded', 'Graded'),
        ('sold', 'Sold')
    ]

    # Dropdown choices for grade tier
    GRADE_CHOICES = [
        ('ungraded', 'Ungraded'),
        ('psa_1', 'PSA 1'),
        ('psa_2', 'PSA 2'),
        ('psa_3', 'PSA 3'),
        ('psa_4', 'PSA 4'),
        ('psa_5', 'PSA 5'),
        ('psa_6', 'PSA 6'),
        ('psa_7', 'PSA 7'),
        ('psa_8', 'PSA 8'),
        ('psa_9', 'PSA 9'),
        ('psa_10', 'PSA 10'),
    ]

    # Links this tracked card to whichever user created it
    # Basic card info
    card_name = models.CharField(max_length=200)           # e.g. "Charizard"
    card_set = models.CharField(max_length=200, blank=True, default='')  # e.g. "Base Set"
    card_year = models.PositiveIntegerField(null=True, blank=True)       # e.g. 1999

    # What grade tier the user cares about
    grade_tier = models.CharField(
        max_length=10, choices=GRADE_CHOICES, default='ungraded',
    )

    # Current tracking status — this is the core of your feature
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='watching',
    )

    # Optional notes the user can add
    notes = models.TextField(blank=True, default='')

    # Auto-set timestamps
    date_added = models.DateTimeField(auto_now_add=True)    # set once on creation
    date_updated = models.DateTimeField(auto_now=True)      # updates every save

    # Placeholder for Story 3 pricing — empty for now
    last_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
    )
    price_trend = models.CharField(
        max_length=10,
        choices=[('up', 'Up'), ('down', 'Down'), ('stable', 'Stable')],
        blank=True, default='',
    )

    # Price the card was sold for
    sold_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
    )

    # Show newest cards first
    class Meta:
        ordering = ['-date_updated']

    # How the card shows up in admin or print statements
    def __str__(self):
        return f"{self.card_name} ({self.get_grade_tier_display()}) — {self.get_status_display()}"


class ValueSnapshot(models.Model):
    """Stores the total collection value at a point in time."""
    total_value = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"${self.total_value} on {self.date}"

class CardPricing(models.Model):
    """Stores pricing data for a card at each grade tier."""
    card_name = models.CharField(max_length=200)
    card_set = models.CharField(max_length=200, blank=True, default='')
    grade_tier = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date_recorded = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-date_recorded']

    def __str__(self):
        return f"{self.card_name} {self.grade_tier} ${self.price} on {self.date_recorded}"