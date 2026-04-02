from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer

from .models import GradeReport, Card, CardCollection
from .serializers import GradeReportSerializer, CardSerializer, CardCollectionSerializer
from .forms import CollectionSettingsForm


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
        cards = collection.cards

        # apply order to cards
        cards = collection.order_collection(collection.sort_order)

        cards = CardSerializer(cards, many=True).data

        for card in cards:
            if float(card['estimated_value']) >= collection.value_threshold:
                card['valuable'] = True
            else:
                card['valuable'] = False

        data = {
            "cards": cards,  # cards in order
            "value_threshold": collection.value_threshold,
        }

        print(data)

        response = Response(
            data=data, template_name="cards/collection.html", status=status.HTTP_200_OK
        )
        return response


class CardViewSet(viewsets.ModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]

    def retrieve(self, request, pk=None):
        """Retrieve a card of a given primary key, uses super retrieve method,
        simply attaching the template to the super's response.
        """
        response = super(CardViewSet, self).retrieve(request, pk=pk)
        response.template_name = "cards/card.html"
        return response

    def update(self, request, pk=None):
        """update a card, only allows changes to the user notes, other fields should not change"""
        card = get_object_or_404(Card, pk=pk)
        card.user_notes = request.POST["user_notes"]
        card.save()
        return self.retrieve(request, pk=pk)


@login_required
def view_collection_settings(request):
    collection = CardCollection.objects.get_or_create(user=request.user)[0]

    form = CollectionSettingsForm(instance=collection)

    if request.method == 'POST':
        form = CollectionSettingsForm(request.POST, instance=collection)
        if form.is_valid():
            form.save()
            return redirect("cards:collection")
    else:
        form = CollectionSettingsForm(instance=collection)

    return render(
        request,
        template_name="cards/collection_settings.html",
        context={"form": form},
    )


# Mock functions, would put them inside a viewset, but that wouldn't be very useful
@login_required
def scan_report_view(request):
    """mock view for card report"""
    return render(
        request,
        template_name="cards/card_report.html",
        context={"user": request.user},
    )


@login_required
def save_report_view(request):
    """mocking function to save report with default info"""

    report = GradeReport.objects.create(grade="No Grade")
    card = Card.objects.create(
        user=request.user,
        name="Invalid Card",
        grading_notes=report,
        picture_path="/static/invalid.jpg",
    )
    card.name += f"-{card.pk}"
    card.save()
    collection = CardCollection.objects.get_or_create(user=request.user)[0]
    collection.cards.add(card)
    collection.save()

    return render(
        request,
        template_name="cards/collection.html",
        context={
            "collection": CardCollectionSerializer(collection).data,
            "cards": CardSerializer(collection.cards, many=True).data,
        },
    )
