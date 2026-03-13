from django.shortcuts import render



# Create your views here.
def index(request):
    return render(request, 'index.html')


def scan_page(request):
    return render(request, "scan.html")


