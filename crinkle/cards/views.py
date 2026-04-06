import base64
import hashlib
import uuid
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response

from .forms import CollectionSettingsForm
from .models import Card, CardCollection, GradeReport, ScannedCard
from .serializers import CardCollectionSerializer, CardSerializer, GradeReportSerializer


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
        """Retrieve the current user's collection in the configured order."""
        collection = self.queryset.get_or_create(user=request.user)[0]
        cards = collection.ordered_collection()

        cards_data = CardSerializer(cards, many=True).data
        for card in cards_data:
            card["is_valuable"] = collection.is_valuable(float(card["estimated_value"]))

        data = {
            "cards": cards_data,
            "value_threshold": collection.value_threshold,
        }

        return Response(
            data=data,
            template_name="cards/collection.html",
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["GET", "POST"])
    def collection_settings(self, request):
        collection = self.queryset.get_or_create(user=request.user)[0]

        if request.method == "POST":
            form = CollectionSettingsForm(request.POST, instance=collection)
            if form.is_valid():
                form.save()
                return redirect("cards:collection")
        else:
            form = CollectionSettingsForm(instance=collection)

        return Response(
            data={"form": form},
            template_name="cards/collection_settings.html",
            status=status.HTTP_200_OK,
        )


class CardViewSet(viewsets.ModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]

    def retrieve(self, request, pk=None):
        card = get_object_or_404(Card, pk=pk, user=request.user)
        serializer = self.get_serializer(card)
        return Response(
            data=serializer.data,
            template_name="cards/card.html",
            status=status.HTTP_200_OK,
        )

    def update(self, request, pk=None):
        """Only allow a user to update notes on their own card."""
        card = get_object_or_404(Card, pk=pk, user=request.user)
        card.user_notes = request.POST.get("user_notes", card.user_notes)
        card.save(update_fields=["user_notes"])
        return self.retrieve(request, pk=pk)


def _ensure_session_key(request):
    if not request.session.session_key:
        request.session.save()
    return request.session.session_key


def _is_guest_session(request):
    return bool(request.session.get("is_guest")) and not request.user.is_authenticated


def _decode_captured_image(data_url):
    if not data_url or "," not in data_url:
        raise ValueError("Missing captured image data.")

    header, encoded = data_url.split(",", 1)
    if not header.startswith("data:image/"):
        raise ValueError("Unsupported image format.")

    extension = "jpg"
    if "image/png" in header:
        extension = "png"
    elif "image/webp" in header:
        extension = "webp"

    return base64.b64decode(encoded), extension


def _store_captured_image(image_bytes, extension):
    media_root = Path(getattr(settings, "MEDIA_ROOT", settings.BASE_DIR / "media"))
    image_dir = media_root / "card_photos"
    image_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex}.{extension}"
    file_path = image_dir / filename
    file_path.write_bytes(image_bytes)

    media_url = getattr(settings, "MEDIA_URL", "/media/")
    return f"{media_url}card_photos/{filename}"


def _estimate_grade(image_bytes):
    digest = hashlib.sha256(image_bytes).hexdigest()
    grade_score = (int(digest[:2], 16) % 4) + 7
    return f"PSA {grade_score}"


def _estimate_value_from_grade(grade):
    score = int(grade.split()[-1])
    return round(score * 25.0, 2)


def _get_scan_for_request(request, scan_id):
    session_key = _ensure_session_key(request)
    scan = get_object_or_404(ScannedCard, pk=scan_id)

    if scan.user_id and request.user.is_authenticated and scan.user_id == request.user.id:
        return scan
    if scan.session_key == session_key:
        return scan

    raise PermissionError("403 Scan Forbidden")


def _build_report_context(request, scan, status_code=200):
    can_save = request.user.is_authenticated and not _is_guest_session(request)
    return {
        "scan": scan,
        "grade": scan.grade,
        "card_name": scan.name,
        "picture_path": scan.picture_path,
        "can_save": can_save,
        "is_guest_session": _is_guest_session(request),
        "status_code": status_code,
    }


def scan_report_view(request):
    """Create a graded scan result from a captured photo and show the report."""
    if request.method == "POST":
        try:
            image_bytes, extension = _decode_captured_image(request.POST.get("captured_image", ""))
        except ValueError:
            messages.error(request, "We could not read that photo. Please retake it.")
            return redirect("scan")

        picture_path = _store_captured_image(image_bytes, extension)
        grade = _estimate_grade(image_bytes)
        estimated_value = _estimate_value_from_grade(grade)
        session_key = _ensure_session_key(request)

        scan = ScannedCard.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_key=session_key,
            name="Scanned Card",
            grade=grade,
            picture_path=picture_path,
            estimated_value=estimated_value,
        )
        request.session["latest_scan_id"] = scan.pk
    else:
        scan_id = request.GET.get("scan_id") or request.session.get("latest_scan_id")
        if not scan_id:
            return redirect("scan")
        try:
            scan = _get_scan_for_request(request, scan_id)
        except PermissionError:
            return HttpResponseForbidden("403 Scan Forbidden")

    return render(request, "cards/card_report.html", _build_report_context(request, scan))


def save_report_view(request):
    """Save the most recent graded scan into the authenticated user's collection."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    scan_id = request.POST.get("scan_id") or request.session.get("latest_scan_id")
    try:
        scan = _get_scan_for_request(request, scan_id)
    except PermissionError:
        return HttpResponseForbidden("403 Scan Forbidden")

    if not request.user.is_authenticated or _is_guest_session(request):
        messages.error(request, "Guests can receive grades, but must log in to save cards.")
        return render(
            request,
            "cards/card_report.html",
            _build_report_context(request, scan, status_code=403),
            status=403,
        )

    report = GradeReport.objects.create(grade=scan.grade)
    card = Card.objects.create(
        user=request.user,
        name=f"{scan.name}-{scan.pk}",
        grading_notes=report,
        picture_path=scan.picture_path,
        user_notes="",
        estimated_value=scan.estimated_value,
    )

    collection = CardCollection.objects.get_or_create(user=request.user)[0]
    collection.cards.add(card)
    collection.save()

    messages.success(request, "Card saved to your collection.")
    return redirect("cards:collection")


@login_required
def delete_card_view(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    card = get_object_or_404(Card, pk=pk, user=request.user)
    collection = CardCollection.objects.get_or_create(user=request.user)[0]
    collection.cards.remove(card)

    grade_report = card.grading_notes
    card.delete()
    if grade_report:
        grade_report.delete()

    messages.success(request, "Card deleted from your collection.")
    return redirect("cards:collection")
