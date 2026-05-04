from django.shortcuts import render


# Create your views here.
def education(request):
    return render(request, "education.html")
