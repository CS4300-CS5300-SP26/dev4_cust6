from django.shortcuts import render, redirect, get_object_or_404
from .forms import SubmissionForm
from .models import Submission


def submission_start(request):
    """Step 1 - select grading service and enter card name"""
    if request.method == 'POST':
        service = request.POST.get('grading_service')
        card_name = request.POST.get('card_name')
        request.session['submission_service'] = service
        request.session['submission_card_name'] = card_name
        return redirect('submission:details')
    return render(request, 'submission/start.html')


def submission_details(request):
    """Step 2 - fill in shipping and payment details"""
    if request.method == 'POST':
        form = SubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            if request.user.is_authenticated:
                submission.user = request.user
            submission.save()
            return redirect('submission:confirmation', pk=submission.pk)
    else:
        initial = {
            'grading_service': request.session.get('submission_service', 'PSA'),
            'card_name': request.session.get('submission_card_name', ''),
        }
        form = SubmissionForm(initial=initial)
    return render(request, 'submission/details.html', {'form': form})


def submission_confirmation(request, pk):
    """Step 3 - show confirmation"""
    submission = get_object_or_404(Submission, pk=pk)
    return render(request, 'submission/confirmation.html', {'submission': submission})