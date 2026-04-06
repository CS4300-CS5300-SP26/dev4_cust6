from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models


class GradeReport(models.Model):
    grade = models.TextField()

    def __str__(self):
        return self.grade


class ScannedCard(models.Model):
    """Temporary scan result created immediately after a photo is captured."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True, db_index=True)
    name = models.CharField(max_length=400, default="Scanned Card")
    grade = models.CharField(max_length=40)
    picture_path = models.CharField(max_length=400)
    estimated_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.grade})"


class Card(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=400)
    date_scanned = models.DateTimeField(auto_now_add=True)
    grading_notes = models.OneToOneField(GradeReport, on_delete=models.CASCADE)

    picture_path = models.CharField(max_length=400)
    user_notes = models.TextField(default="", blank=True)

    estimated_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=50.00,
        validators=[MinValueValidator(0)],
    )

    def __str__(self):
        return self.name


class CardCollection(models.Model):
    SORT_CHOICES = [
        ("name", "Name"),
        ("date_scanned", "Date Scanned"),
        ("grading_notes", "Grade"),
        ("-name", "Name Descending"),
        ("-date_scanned", "Date Scanned Descending"),
        ("-grading_notes", "Grade Descending"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cards = models.ManyToManyField(Card)

    sort_order = models.CharField(max_length=400, choices=SORT_CHOICES, default="name")
    value_threshold = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=100.00,
        validators=[MinValueValidator(0)],
    )

    def __str__(self):
        return f"Collection of {self.user.username}"

    def ordered_collection(self):
        """Return the user's cards in the configured order."""
        cards = self.cards.all()

        if hasattr(Card, self.sort_order.lstrip("-")):
            cards = cards.order_by(self.sort_order)

        return cards

    def is_valuable(self, value):
        """Check whether a card value meets the collection threshold."""
        return value >= self.value_threshold
