from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
def cards_view(request):
    return render(request, template_name='cards/base.html')