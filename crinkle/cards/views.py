from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from cards.models import Card, CardCollection


@login_required
def collection_view(request):
    collection = CardCollection.objects.get_or_create(user=request.user)
    return render(request,
                  template_name='cards/collection.html',
                  context={'collection': collection[0]},
                  )
