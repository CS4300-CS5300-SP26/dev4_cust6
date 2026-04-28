from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class GradeReport(models.Model):
    grade = models.TextField(default="")
    corners = models.TextField(default="")
    edges = models.TextField(default="")
    centering = models.TextField(default="")
    surface = models.TextField(default="")

    def __str__(self):
        return self.grade


class Card(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=400)
    date_scanned = models.DateTimeField(auto_now_add=True)
    grading_notes = models.OneToOneField(GradeReport, on_delete=models.CASCADE)

    picture_path = models.CharField(max_length=400)
    user_notes = models.TextField()

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
        """order card collection by sort_order parameter

        Args:
            sort_order (str): order of sort

        Returns:
            QS_: query set of ordered_cards
        """
        cards = self.cards.all()

        # if the card model has the attribute in sort order
        # then apply it
        if hasattr(Card, self.sort_order.lstrip("-")):
            cards = cards.order_by(self.sort_order)

        return cards
    
    def is_valuable(self, value):
        """Helper to check and return if value is valuable

        Args:
            value (Decimal): value to check if valuable

        Returns:
            bool: flag indicating if value is valuable according to colllection
        """
        return value >= self.value_threshold
