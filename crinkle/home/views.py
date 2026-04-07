from django.shortcuts import render
from .models import Card
from scan.views import scan_page

# Create your views here.
def index(request):
    return render(request, 'index.html')

def history(request):
    cards = Card.objects.all().order_by('-date_scanned')
    return render(request, 'history.html', {'cards': cards})
