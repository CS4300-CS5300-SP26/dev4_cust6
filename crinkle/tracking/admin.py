from django.contrib import admin
from .models import TrackedCard


@admin.register(TrackedCard)
class TrackedCardAdmin(admin.ModelAdmin):
    # Columns shown in the admin list view
    list_display = (
        "card_name",
        "card_set",
        "grade_tier",
        "status",
        "date_updated",
    )

    # Sidebar filters
    list_filter = ("status", "grade_tier")

    # Search bar searches these fields
    search_fields = ("card_name", "card_set")
