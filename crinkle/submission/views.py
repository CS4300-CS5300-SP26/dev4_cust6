import stripe
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .forms import SubmissionForm
from .models import Submission

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', '')

GRADING_PRICES = {
    'PSA': 2500,  # $25.00 in cents
    'BGS': 3000,  # $30.00 in cents
}


def submission_start(request):
    if request.method == 'POST':
        service = request.POST.get('grading_service')
        card_name = request.POST.get('card_name')
        request.session['submission_service'] = service
        request.session['submission_card_name'] = card_name
        return redirect('submission:details')
    return render(request, 'submission/start.html')


def submission_details(request):
    if request.method == 'POST':
        form = SubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            if request.user.is_authenticated:
                submission.user = request.user
            submission.save()
            request.session['submission_pk'] = submission.pk
            return redirect('submission:checkout', pk=submission.pk)
    else:
        initial = {
            'grading_service': request.session.get('submission_service', 'PSA'),
            'card_name': request.session.get('submission_card_name', ''),
        }
        form = SubmissionForm(initial=initial)
    return render(request, 'submission/details.html', {'form': form})


def submission_checkout(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    price = GRADING_PRICES.get(submission.grading_service, 2500)

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': f'{submission.grading_service} Grading — {submission.card_name}',
                },
                'unit_amount': price,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri(f'/submission/success/{pk}/'),
        cancel_url=request.build_absolute_uri(f'/submission/cancel/{pk}/'),
    )

    submission.stripe_session_id = session.id
    submission.save()

    return redirect(session.url, code=303)


def submission_success(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    submission.paid = True
    submission.save()
    return render(request, 'submission/confirmation.html', {'submission': submission})


def submission_cancel(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    submission.delete()
    return redirect('submission:start')


def submission_confirmation(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    return render(request, 'submission/confirmation.html', {'submission': submission})