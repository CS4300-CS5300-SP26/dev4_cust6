import os

import stripe
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import SubmissionForm
from .models import Submission

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")

GRADING_PRICES = {
    "PSA": 2500,  # $25.00 in cents
    "BGS": 3000,  # $30.00 in cents
}


def _user_submission_or_404(user, pk):
    """Return only submissions owned by the authenticated user."""
    return get_object_or_404(Submission, pk=pk, user=user)


@login_required
def submission_start(request):
    if request.method == "POST":
        service = request.POST.get("grading_service")
        card_name = request.POST.get("card_name")
        request.session["submission_service"] = service
        request.session["submission_card_name"] = card_name
        return redirect("submission:details")
    return render(request, "submission/start.html")


@login_required
def submission_details(request):
    if request.method == "POST":
        form = SubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.user = request.user
            submission.save()
            request.session["submission_pk"] = submission.pk
            return redirect("submission:checkout", pk=submission.pk)
    else:
        initial = {
            "grading_service": request.session.get(
                "submission_service", "PSA"
            ),
            "card_name": request.session.get("submission_card_name", ""),
        }
        form = SubmissionForm(initial=initial)
    return render(request, "submission/details.html", {"form": form})


@login_required
def submission_checkout(request, pk):
    submission = _user_submission_or_404(request.user, pk)
    price = GRADING_PRICES.get(submission.grading_service, 2500)

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": (
                            f"{submission.grading_service} Grading — "
                            f"{submission.card_name}"
                        ),
                    },
                    "unit_amount": price,
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=request.build_absolute_uri(f"/submission/success/{pk}/"),
        cancel_url=request.build_absolute_uri(f"/submission/cancel/{pk}/"),
    )

    submission.stripe_session_id = session.id
    submission.save(update_fields=["stripe_session_id"])

    return redirect(session.url, code=303)


@login_required
def submission_success(request, pk):
    submission = _user_submission_or_404(request.user, pk)
    submission.paid = True
    submission.save(update_fields=["paid"])
    return render(
        request, "submission/confirmation.html", {"submission": submission}
    )


@login_required
def submission_cancel(request, pk):
    submission = _user_submission_or_404(request.user, pk)
    submission.delete()
    return redirect("submission:start")


@login_required
def submission_confirmation(request, pk):
    submission = _user_submission_or_404(request.user, pk)
    return render(
        request, "submission/confirmation.html", {"submission": submission}
    )
