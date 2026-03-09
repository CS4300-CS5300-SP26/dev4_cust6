from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import GradeReport, Card, CardCollection
from datetime import datetime



@login_required
def collection_view(request):
    collection = CardCollection.objects.get_or_create(user=request.user)[0]
    cards = collection.cards.all()

    if 'order' in request.GET:
        match request.GET['order']:
            case 'date':
                cards = cards.order_by('date_scanned')
                print(cards.first().date_scanned)
            case 'date-dsc':
                cards = cards.order_by('-date_scanned')
                print(cards.first().date_scanned)
            case 'name':
                cards = cards.order_by('name')
            case 'name-dsc':
                cards = cards.order_by('-name')
            case 'grade':
                cards = cards.order_by('grading_notes')
            case 'grade-dsc':
                cards = cards.order_by('-grading_notes')

    return render(request,
                  template_name='cards/collection.html',
                  context={'collection': collection,
                           'cards': cards,
                           },
                  )


@login_required
def card_view(request, card_pk):
    card = get_object_or_404(Card, pk=card_pk)

    return render(request,
                  template_name='cards/card.html',
                  context={'card': card,
                           },
                  )


@login_required
def save_card_view(request, card_pk):
    card = get_object_or_404(Card, pk=card_pk)

    card.user_notes = request.POST['user_notes']

    print(card.user_notes)

    card.save()
    return card_view(request, card_pk=card_pk)


@login_required
def scan_report_view(request):
    return render(request,
                  template_name='cards/card_report.html',
                  context={'user': request.user},
                  )


@login_required
def save_report_view(request):
    """mocking function to save report with default info
    """

    report = GradeReport.objects.create(grade="No Grade")
    card = Card.objects.create(name="Invalid Card",
                               grading_notes=report,
                               picture_path="/static/invalid.png",
                               )
    card.name += f'-{card.pk}'
    card.save()
    collection = CardCollection.objects.get_or_create(user=request.user)[0]
    collection.cards.add(card)
    collection.save()

    return collection_view(request)
