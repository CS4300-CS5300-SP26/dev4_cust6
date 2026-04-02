from django.db import models
from django.contrib.auth.models import User


class GradeReport(models.Model):
    grade = models.TextField()

    def __str__(self):
        return self.grade


class Card(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=400)
    date_scanned = models.DateTimeField(auto_now_add=True)
    grading_notes = models.OneToOneField(GradeReport, on_delete=models.CASCADE)

    picture_path = models.CharField(max_length=400)
    user_notes = models.TextField()

    def __str__(self):
        return self.name


class CardCollection(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cards = models.ManyToManyField(Card)

    sort_order = models.CharField(max_length=400, default="name")
    value_threshold = models.DecimalField(max_digits=12, decimal_places=2, default=100)

    def __str__(self):
        return f"Collection of {self.user.username}"

    def order_collection(self, sort_order):
        """order card collection by sort_order parameter

        Args:
            sort_order (str): order of sort

        Returns:
            QS_: query set of ordered_cards
        """
        cards = self.cards.all()

        # if the card model has the attribute in sort order
        # then apply it
        if hasattr(Card, sort_order.lstrip("-")):
            cards = cards.order_by(sort_order)

        return cards
