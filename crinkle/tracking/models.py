from django.db import models
from django.conf import settings
from datetime import date


class TrackedCard(models.Model):
    STATUS_CHOICES = [
        ('watching', 'Watching'),
        ('sold', 'Sold'),
    ]
    GRADE_CHOICES = [
        ('ungraded', 'Ungraded'),
        ('near_mint', 'Near Mint'),
        ('lightly_played', 'Lightly Played'),
        ('moderately_played', 'Moderately Played'),
        ('heavily_played', 'Heavily Played'),
        ('damaged', 'Damaged'),
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
    card_name = models.CharField(max_length=200)
    card_set = models.CharField(max_length=200, blank=True, default='')
    card_year = models.PositiveIntegerField(null=True, blank=True)
    grade_tier = models.CharField(
        max_length=20, choices=GRADE_CHOICES, default='ungraded',
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='watching',
    )
    notes = models.TextField(blank=True, default='')
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    last_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
    )
    price_trend = models.CharField(
        max_length=10,
        choices=[('up', 'Up'), ('down', 'Down'), ('stable', 'Stable')],
        blank=True, default='',
    )
    sold_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
    )
    target_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
    )

    class Meta:
        ordering = ['-date_updated']

    def __str__(self):
        return f"{self.card_name} ({self.get_grade_tier_display()}) — {self.get_status_display()}"


class ValueSnapshot(models.Model):
    total_value = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"${self.total_value} on {self.date}"


class CardPricing(models.Model):
    CONDITION_CHOICES = [
        ('near_mint', 'Near Mint'),
        ('lightly_played', 'Lightly Played'),
        ('moderately_played', 'Moderately Played'),
        ('heavily_played', 'Heavily Played'),
        ('damaged', 'Damaged'),
    ]
    card_name = models.CharField(max_length=200)
    card_set = models.CharField(max_length=200, blank=True, default='')
    tcg_player_id = models.CharField(max_length=50, blank=True, default='')
    image_url = models.URLField(blank=True, default='')
    grade_tier = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date_recorded = models.DateField(default=date.today)

    class Meta:
        ordering = ['-date_recorded']

    def __str__(self):
        return f"{self.card_name} {self.grade_tier} ${self.price} on {self.date_recorded}"