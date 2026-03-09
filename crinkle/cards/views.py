from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.renderers import (TemplateHTMLRenderer,
                                      BrowsableAPIRenderer,
                                      JSONRenderer,
                                      )

from .models import GradeReport, Card, CardCollection
from .serializers import GradeReportSerializer, CardSerializer, CardCollectionSerializer


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
        """Override super's retrieve if one doesn't exist create one
        """
        collection = self.queryset.get_or_create(user=request.user)[0]
        cards = collection.cards.all()

        if 'order' in request.GET:
            cards = cards.order_by(request.GET['order'])

        data = {
            'collection': self.serializer_class(collection).data,
            'cards': CardSerializer(cards, many=True).data,
        }

        response = Response(data=data,
                            template_name='cards/collection.html',
                            status=status.HTTP_200_OK)
        return response


class CardViewSet(viewsets.ModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]


@login_required
def card_view(request, card_pk):
    """View for singular card
    """
    card = get_object_or_404(Card, pk=card_pk)

    return render(request,
                  template_name='cards/card.html',
                  context={'card': card,
                           },
                  )


@login_required
def save_card_view(request, card_pk):
    """View to save a card
    """
    card = get_object_or_404(Card, pk=card_pk)

    card.user_notes = request.POST['user_notes']

    print(card.user_notes)

    card.save()
    return card_view(request, card_pk=card_pk)


@login_required
def scan_report_view(request):
    """mock view for card report
    """
    return render(request,
                  template_name='cards/card_report.html',
                  context={'user': request.user},
                  )


@login_required
def save_report_view(request):
    """mocking function to save report with default info
    """

    report = GradeReport.objects.create(grade="No Grade")
    card = Card.objects.create(user=request.user,
                               name="Invalid Card",
                               grading_notes=report,
                               picture_path="/static/invalid.png",
                               )
    card.name += f'-{card.pk}'
    card.save()
    collection = CardCollection.objects.get_or_create(user=request.user)[0]
    collection.cards.add(card)
    collection.save()

    return collection_view(request)
