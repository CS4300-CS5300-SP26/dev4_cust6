from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.templatetags.static import static
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.cache import cache
from django.views.decorators.http import require_POST
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from .ai_grading import analyze_card_with_gemini
from .models import GradeReport, Card, CardCollection
from .serializers import (
    GradeReportSerializer,
    CardSerializer,
    CardCollectionSerializer,
)
from .forms import CollectionSettingsForm

import base64
import binascii
import io
import uuid

from PIL import Image, UnidentifiedImageError

CAPTURED_SCAN_SESSION_KEY = "captured_scan_image"
ALLOWED_IMAGE_MIME_TYPES = {
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/gif": "gif",
    "image/webp": "webp",
}
MAX_CAPTURED_IMAGE_BYTES = 5 * 1024 * 1024
AI_SCAN_RATE_LIMIT = 5
AI_SCAN_RATE_WINDOW_SECONDS = 60 * 60


def _client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def _rate_limit_exceeded(key, limit, window_seconds):
    if cache.add(key, 1, window_seconds):
        return False
    try:
        return cache.incr(key) > limit
    except ValueError:
        cache.set(key, 1, window_seconds)
        return False


def _ai_scan_rate_limit_exceeded(request):
    if request.user.is_authenticated:
        identity = f"user:{request.user.pk}"
    else:
        identity = f"ip:{_client_ip(request)}"
    return _rate_limit_exceeded(
        f"ai-scan:{identity}",
        AI_SCAN_RATE_LIMIT,
        AI_SCAN_RATE_WINDOW_SECONDS,
    )


class GradeReportViewSet(viewsets.ModelViewSet):
    queryset = GradeReport.objects.all()
    serializer_class = GradeReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]


class CardCollectionViewSet(viewsets.ModelViewSet):
    queryset = CardCollection.objects.all()
    serializer_class = CardCollectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]

    def retrieve(self, request):
        """Retrieve the authenticated user's ordered collection."""
        collection = self.queryset.get_or_create(user=request.user)[0]
        cards = collection.ordered_collection()

        cards_data = CardSerializer(cards, many=True).data

        for card in cards_data:
            card["is_valuable"] = collection.is_valuable(
                float(card["estimated_value"])
            )

        data = {
            "cards": cards_data,
            "value_threshold": collection.value_threshold,
        }

        response = Response(
            data=data,
            template_name="cards/collection.html",
            status=status.HTTP_200_OK,
        )
        return response

    @action(detail=False, methods=["GET", "POST"])
    def collection_settings(self, request):
        collection = self.queryset.get_or_create(user=request.user)[0]

        form = CollectionSettingsForm(instance=collection)

        if request.method == "POST":
            form = CollectionSettingsForm(request.POST, instance=collection)
            if form.is_valid():
                form.save()
                return redirect("cards:collection")
        else:
            form = CollectionSettingsForm(instance=collection)

        response = Response(
            data={"form": form},
            template_name="cards/collection_settings.html",
            status=status.HTTP_200_OK,
        )

        return response


class CardViewSet(viewsets.ModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]

    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)

    @action(detail=False, methods=["GET"])
    def history(self, request):
        cards = self.queryset.filter(user=request.user.id).order_by(
            "date_scanned"
        )

        cards_data = CardSerializer(cards, many=True).data

        response = Response(
            data={"cards": cards_data},
            template_name="history.html",
            status=status.HTTP_200_OK,
        )
        return response

    def retrieve(self, request, pk=None):
        """Retrieve a card of a given primary key."""
        response = super(CardViewSet, self).retrieve(request, pk=pk)
        response.template_name = "cards/card.html"

        if response.data["user"] == request.user.id:
            response.template_name = "cards/card.html"
        else:
            response = HttpResponseForbidden("403 Card Forbidden")

        return response

    def update(self, request, pk=None):
        """Update notes only on cards owned by the authenticated user."""
        card = get_object_or_404(Card, pk=pk, user=request.user)
        card.user_notes = request.POST.get("user_notes", "")
        card.save(update_fields=["user_notes"])
        return self.retrieve(request, pk=pk)


def _captured_image_from_request(request):
    captured_image = request.POST.get("captured_image") or request.session.get(
        CAPTURED_SCAN_SESSION_KEY
    )

    if captured_image:
        request.session[CAPTURED_SCAN_SESSION_KEY] = captured_image

    return captured_image


def _save_captured_image(data_url):
    if not data_url or ";base64," not in data_url:
        return static("invalid.jpg")

    header, encoded_image = data_url.split(";base64,", 1)
    if not header.startswith("data:"):
        return static("invalid.jpg")

    mime_type = header[5:].split(";", 1)[0].lower()
    file_extension = ALLOWED_IMAGE_MIME_TYPES.get(mime_type)
    if not file_extension:
        return static("invalid.jpg")

    try:
        image_bytes = base64.b64decode(encoded_image, validate=True)
    except (binascii.Error, ValueError):
        return static("invalid.jpg")

    if len(image_bytes) > MAX_CAPTURED_IMAGE_BYTES:
        return static("invalid.jpg")

    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.verify()
    except (UnidentifiedImageError, OSError, ValueError):
        return static("invalid.jpg")

    file_name = f"scans/{uuid.uuid4()}.{file_extension}"
    saved_path = default_storage.save(file_name, ContentFile(image_bytes))

    return f"{settings.MEDIA_URL}{saved_path}"


GRADE_SESSION_KEY = "card_grade_result"


def scan_report_view(request):
    """Show AI grading reports for authenticated users only."""
    captured_image = _captured_image_from_request(request)

    # run AI analysis on POST (coming from scan page)
    if request.method == "POST" and captured_image:
        if _ai_scan_rate_limit_exceeded(request):
            return HttpResponse(
                "Too many AI grading requests. Please try again later.",
                status=429,
            )
        grade_result = analyze_card_with_gemini(captured_image)
        request.session[GRADE_SESSION_KEY] = grade_result
        request.session.modified = True
    else:
        grade_result = request.session.get(GRADE_SESSION_KEY, {})

    return render(
        request,
        template_name="cards/card_report.html",
        context={
            "user": request.user,
            "user_label": (
                request.user.username
                if request.user.is_authenticated
                else "Guest"
            ),
            "report_image": captured_image or static("invalid.jpg"),
            "can_save_to_collection": request.user.is_authenticated,
            "quality_ok": grade_result.get("quality_ok", True),
            "quality_issues": grade_result.get("quality_issues", []),
            "psa_grade": grade_result.get("psa_grade", "—"),
            "card_name": grade_result.get("card_name", "Unknown Card"),
            "card_set": grade_result.get("card_set", ""),
            "card_year": grade_result.get("card_year", ""),
            "corners": grade_result.get("corners", ""),
            "edges": grade_result.get("edges", ""),
            "centering": grade_result.get("centering", ""),
            "surface": grade_result.get("surface", ""),
        },
    )


@login_required
def save_report_view(request):
    """Save the latest captured scan to the authenticated user's collection."""
    grade_result = request.session.get(GRADE_SESSION_KEY, {})
    captured_image = request.session.get(CAPTURED_SCAN_SESSION_KEY)
    if not captured_image:
        return redirect("cards:scan_report")

    report = GradeReport.objects.create(
        grade=grade_result.get("psa_grade", "—"),
        corners=grade_result.get("corners", ""),
        edges=grade_result.get("edges", ""),
        centering=grade_result.get("centering", ""),
        surface=grade_result.get("surface", ""),
    )
    picture_path = _save_captured_image(captured_image)

    card = Card.objects.create(
        user=request.user,
        name=grade_result.get("card_name", "Unknown Card"),
        set_name=grade_result.get("card_set", ""),
        year=grade_result.get("card_year", ""),
        grading_notes=report,
        picture_path=picture_path,
        user_notes="",
    )
    card.save()

    collection = CardCollection.objects.get_or_create(user=request.user)[0]
    collection.cards.add(card)

    request.session.pop(CAPTURED_SCAN_SESSION_KEY, None)

    return redirect("cards:collection")


@login_required
@require_POST
def delete_card_view(request, pk):
    """Remove a card from the authenticated user's collection and delete it."""
    card = get_object_or_404(Card, pk=pk, user=request.user)
    collection = CardCollection.objects.get_or_create(user=request.user)[0]

    if collection.cards.filter(pk=card.pk).exists():
        collection.cards.remove(card)

    card.delete()

    return redirect("cards:collection")
