from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import TrackedCard, CardPricing
from .forms import TrackedCardForm


@login_required
def tracking_list(request):
    tracked_cards = TrackedCard.objects.filter(user=request.user)

    status_filter = request.GET.get("status")
    if status_filter and status_filter in dict(TrackedCard.STATUS_CHOICES):
        tracked_cards = tracked_cards.filter(status=status_filter)

    cards_with_data = []
    for card in tracked_cards:
        pricing = (
            CardPricing.objects.filter(
                card_name=card.card_name,
                card_set=card.card_set,
                grade_tier=card.grade_tier,
            )
            .order_by("-date_recorded")
            .first()
        )

        if not pricing:
            pricing = (
                CardPricing.objects.filter(
                    card_name=card.card_name,
                    card_set=card.card_set,
                )
                .order_by("-date_recorded")
                .first()
            )

        grade_tier_for_history = (
            card.grade_tier
            if pricing
            and CardPricing.objects.filter(
                card_name=card.card_name,
                card_set=card.card_set,
                grade_tier=card.grade_tier,
            ).exists()
            else (pricing.grade_tier if pricing else "")
        )

        history = CardPricing.objects.filter(
            card_name=card.card_name,
            card_set=card.card_set,
            grade_tier=grade_tier_for_history,
        ).order_by("date_recorded")

        trend = None
        if history.count() >= 2:
            oldest = history.first().price
            newest = history.last().price
            if newest > oldest:
                trend = "up"
            elif newest < oldest:
                trend = "down"
            else:
                trend = "stable"

        cards_with_data.append(
            {
                "card": card,
                "image_url": pricing.image_url if pricing else "",
                "market_price": pricing.price if pricing else None,
                "trend": trend,
            }
        )

    context = {
        "tracked_cards": cards_with_data,
        "status_choices": TrackedCard.STATUS_CHOICES,
        "current_filter": status_filter or "all",
        "sold_total": TrackedCard.objects.filter(user=request.user, status="sold")
        .exclude(sold_price__isnull=True)
        .aggregate(total=models.Sum("sold_price"))["total"]
        or 0,
    }
    return render(request, "tracking/tracking_list.html", context)


@login_required
def tracking_detail(request, pk):
    card = get_object_or_404(TrackedCard, pk=pk, user=request.user)

    pricing = (
        CardPricing.objects.filter(
            card_name=card.card_name,
            card_set=card.card_set,
            grade_tier=card.grade_tier,
        )
        .order_by("-date_recorded")
        .first()
    )

    if not pricing:
        pricing = (
            CardPricing.objects.filter(
                card_name=card.card_name,
                card_set=card.card_set,
            )
            .order_by("-date_recorded")
            .first()
        )

    history = CardPricing.objects.filter(
        card_name=card.card_name,
        card_set=card.card_set,
        grade_tier=pricing.grade_tier if pricing else "",
    ).order_by("date_recorded")

    trend = None
    if history.count() >= 2:
        oldest = history.first().price
        newest = history.last().price
        if newest > oldest:
            trend = "up"
        elif newest < oldest:
            trend = "down"
        else:
            trend = "stable"

    return render(
        request,
        "tracking/tracking_detail.html",
        {
            "card": card,
            "image_url": pricing.image_url if pricing else "",
            "market_price": pricing.price if pricing else None,
            "trend": trend,
        },
    )


@login_required
def tracking_add(request):
    if request.method == "POST":
        form = TrackedCardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.user = request.user
            card.save()
            messages.success(
                request, f"Now tracking {form.cleaned_data['card_name']}!"
            )
            return redirect("tracking:list")
    else:
        form = TrackedCardForm()

    return render(
        request,
        "tracking/tracking_form.html",
        {
            "form": form,
            "action": "Add",
        },
    )


@login_required
def tracking_edit(request, pk):
    card = get_object_or_404(TrackedCard, pk=pk, user=request.user)

    if request.method == "POST":
        form = TrackedCardForm(request.POST, instance=card)
        if form.is_valid():
            form.save()
            messages.success(request, f"Updated {card.card_name}.")
            return redirect("tracking:detail", pk=card.pk)
    else:
        form = TrackedCardForm(instance=card)

    return render(
        request,
        "tracking/tracking_form.html",
        {
            "form": form,
            "action": "Edit",
            "card": card,
        },
    )


@login_required
def tracking_delete(request, pk):
    card = get_object_or_404(TrackedCard, pk=pk, user=request.user)

    if request.method == "POST":
        card_name = card.card_name
        card.delete()
        messages.success(request, f"Stopped tracking {card_name}.")
        return redirect("tracking:list")

    return render(request, "tracking/tracking_delete.html", {"card": card})


@login_required
def market_search(request):
    query = request.GET.get("q", "")
    set_filter = request.GET.get("set", "")
    sort = request.GET.get("sort", "name")
    grade_filter = request.GET.get("grade", "")

    if query:
        cards_qs = CardPricing.objects.filter(card_name__icontains=query)
    else:
        cards_qs = CardPricing.objects.all()

    if set_filter:
        cards_qs = cards_qs.filter(card_set=set_filter)

    unique_cards = cards_qs.values(
        "card_name", "card_set", "tcg_player_id"
    ).distinct()

    card_list = []
    seen = set()
    for card in unique_cards:
        key = (
            card["tcg_player_id"] or f"{card['card_name']}_{card['card_set']}"
        )
        if key in seen:
            continue
        seen.add(key)

        tier = grade_filter if grade_filter else "near_mint"
        latest = (
            CardPricing.objects.filter(
                card_name=card["card_name"],
                card_set=card["card_set"],
                grade_tier=tier,
            )
            .order_by("-date_recorded")
            .first()
        )

        card_list.append(
            {
                "card_name": card["card_name"],
                "card_set": card["card_set"],
                "price": latest.price if latest else None,
                "image_url": latest.image_url if latest else "",
            }
        )

    if sort == "-name":
        card_list.sort(key=lambda c: c["card_name"], reverse=True)
    elif sort == "price_low":
        card_list.sort(key=lambda c: c["price"] or 0)
    elif sort == "price_high":
        card_list.sort(key=lambda c: c["price"] or 0, reverse=True)
    else:
        card_list.sort(key=lambda c: c["card_name"])

    sets = list(
        CardPricing.objects.values_list("card_set", flat=True)
        .distinct()
        .order_by("card_set")
    )

    context = {
        "query": query,
        "cards": card_list,
        "sets": sets,
        "current_set": set_filter,
        "current_sort": sort,
    }
    return render(request, "tracking/market_search.html", context)


@login_required
def card_pricing(request):
    card_name = request.GET.get("name", "")
    card_set = request.GET.get("set", "")

    if not card_name:
        return redirect("tracking:market")

    tiers = [
        "near_mint",
        "lightly_played",
        "moderately_played",
        "heavily_played",
        "damaged",
    ]
    tier_labels = {
        "near_mint": "Near Mint",
        "lightly_played": "Lightly Played",
        "moderately_played": "Moderately Played",
        "heavily_played": "Heavily Played",
        "damaged": "Damaged",
    }

    tier_prices = []
    for tier in tiers:
        latest = (
            CardPricing.objects.filter(
                card_name=card_name,
                card_set=card_set,
                grade_tier=tier,
            )
            .order_by("-date_recorded")
            .first()
        )
        tier_prices.append(
            {
                "tier": tier,
                "label": tier_labels[tier],
                "price": latest.price if latest else None,
                "image_url": latest.image_url if latest else "",
            }
        )

    selected_tier = request.GET.get("tier", "near_mint")
    history = CardPricing.objects.filter(
        card_name=card_name,
        card_set=card_set,
        grade_tier=selected_tier,
    ).order_by("date_recorded")

    chart_dates = [h.date_recorded.strftime("%b %d") for h in history]
    chart_prices = [float(h.price) for h in history]

    compare_data = []
    for i in range(len(tier_prices) - 1):
        if tier_prices[i]["price"] and tier_prices[i + 1]["price"]:
            delta = tier_prices[i + 1]["price"] - tier_prices[i]["price"]
            compare_data.append(
                {
                    "from": tier_prices[i]["label"],
                    "to": tier_prices[i + 1]["label"],
                    "delta": delta,
                }
            )

    image_url = tier_prices[0]["image_url"] if tier_prices else ""

    context = {
        "card_name": card_name,
        "card_set": card_set,
        "tier_prices": tier_prices,
        "chart_dates": chart_dates,
        "chart_prices": chart_prices,
        "selected_tier": selected_tier,
        "tier_labels": tier_labels,
        "compare_data": compare_data,
        "image_url": image_url,
    }
    return render(request, "tracking/card_pricing.html", context)


@login_required
def market_watch(request):
    if request.method == "POST":
        card_name = request.POST.get("card_name", "")
        card_set = request.POST.get("card_set", "")
        grade_tier = request.POST.get("grade_tier", "ungraded")
        if card_name:
            existing = TrackedCard.objects.filter(
                user=request.user, card_name=card_name, card_set=card_set
            ).first()
            if not existing:
                TrackedCard.objects.create(
                    user=request.user,
                    card_name=card_name,
                    card_set=card_set,
                    grade_tier=grade_tier,
                    status="watching",
                )
    return redirect("tracking:market")


@login_required
def market_compare(request):
    names = request.GET.getlist("name")
    sets = request.GET.getlist("set")

    cards = []
    tiers = [
        "near_mint",
        "lightly_played",
        "moderately_played",
        "heavily_played",
        "damaged",
    ]
    tier_labels = {
        "near_mint": "Near Mint",
        "lightly_played": "Lightly Played",
        "moderately_played": "Moderately Played",
        "heavily_played": "Heavily Played",
        "damaged": "Damaged",
    }

    for card_name, card_set in zip(names, sets):
        tier_prices = []
        image_url = ""
        for tier in tiers:
            latest = (
                CardPricing.objects.filter(
                    card_name=card_name,
                    card_set=card_set,
                    grade_tier=tier,
                )
                .order_by("-date_recorded")
                .first()
            )
            if latest and not image_url:
                image_url = latest.image_url
            tier_prices.append(
                {
                    "tier": tier,
                    "label": tier_labels[tier],
                    "price": latest.price if latest else None,
                }
            )
        cards.append(
            {
                "card_name": card_name,
                "card_set": card_set,
                "image_url": image_url,
                "tier_prices": tier_prices,
            }
        )

    context = {
        "cards": cards,
        "tiers": tiers,
        "tier_labels": tier_labels,
    }
    return render(request, "tracking/market_compare.html", context)
