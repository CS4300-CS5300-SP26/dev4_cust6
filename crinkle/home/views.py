from django.shortcuts import render
from scan.views import scan_page

# Create your views here.
def index(request):
    return render(request, 'index.html')
