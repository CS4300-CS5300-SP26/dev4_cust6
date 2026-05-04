from django.shortcuts import render


def scan_page(request):
    return render(request, "scan/scan.html")
