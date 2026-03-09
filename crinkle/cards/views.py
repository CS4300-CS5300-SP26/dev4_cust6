from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from cards.models import GradeReport, Card, CardCollection


@login_required
def collection_view(request):
    collection = CardCollection.objects.get_or_create(user=request.user)[0]
    return render(request,
                  template_name='cards/collection.html',
                  context={'collection': collection,
                           'cards': collection.cards.all()
                           },
                  )


@login_required
def card_view(request, card_pk):
    card = get_object_or_404(Card, pk=card_pk)

    return render(request,
                  template_name='cards/card.html',
                  context={'card': card},
                  )


@login_required
def save_card_view(request, card_pk):
    card = get_object_or_404(Card, pk=card_pk)

    print(request)

    return render(request,
                  template_name='cards/card.html',
                  context={'card': card},
                  )


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
    collection = CardCollection.objects.get_or_create(user=request.user)[0]
    collection.cards.add(card)
    collection.save()

    return collection_view(request)
