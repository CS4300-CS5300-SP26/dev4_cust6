from django.shortcuts import render
from .models import Card

# Create your views here.
def index(request):
    return render(request, 'index.html')

def history(request):
    cards = Card.objects.all().order_by('-scanned_at')
    return render(request, 'history.html', {'cards': cards})