from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.templatetags.static import static
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.views.decorators.http import require_POST
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from .ai_grading import analyze_card_with_gemini
from .models import GradeReport, Card, CardCollection
from .serializers import GradeReportSerializer, CardSerializer, CardCollectionSerializer
from .forms import CollectionSettingsForm

import base64
import uuid


CAPTURED_SCAN_SESSION_KEY = "captured_scan_image"


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
        """If the user is authenticated, retrieve their collection in the order (if specified)"""
        collection = self.queryset.get_or_create(user=request.user)[0]
        cards = collection.ordered_collection()

        cards_data = CardSerializer(cards, many=True).data

        for card in cards_data:
            card["is_valuable"] = collection.is_valuable(float(card["estimated_value"]))

        data = {
            "cards": cards_data,
            "value_threshold": collection.value_threshold,
        }

        response = Response(
            data=data, template_name="cards/collection.html", status=status.HTTP_200_OK
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

    @action(detail=False, methods=["GET"])
    def history(self, request):
        cards = self.queryset.filter(user=request.user.id)

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
        """Update a card, only allows changes to the user notes."""
        card = get_object_or_404(Card, pk=pk)
        card.user_notes = request.POST["user_notes"]
        card.save()
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
    file_extension = header.split("/")[-1] if "/" in header else "jpg"
    file_name = f"scans/{uuid.uuid4()}.{file_extension}"

    image_bytes = base64.b64decode(encoded_image)
    saved_path = default_storage.save(file_name, ContentFile(image_bytes))

    return f"{settings.MEDIA_URL}{saved_path}"


GRADE_SESSION_KEY = "card_grade_result"

def scan_report_view(request):
    """AI grading report that supports guest grading and authenticated saving."""
    captured_image = _captured_image_from_request(request)

    # run AI analysis on POST (coming from scan page)
    if request.method == 'POST' and captured_image:
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
            "user_label": request.user.username if request.user.is_authenticated else "Guest",
            "report_image": captured_image or static("invalid.jpg"),
            "can_save_to_collection": request.user.is_authenticated,
            "psa_grade": grade_result.get("psa_grade", "—"),
            "card_name": grade_result.get("card_name", "Unknown Card"),
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

    report = GradeReport.objects.create(grade=grade_result.get("psa_grade", "—"))
    picture_path = _save_captured_image(captured_image)

    card = Card.objects.create(
        user=request.user,
        name="Scanned Card",
        grading_notes=report,
        picture_path=picture_path,
        user_notes="",
    )
    card.name = f"{card.name}-{card.pk}"
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
