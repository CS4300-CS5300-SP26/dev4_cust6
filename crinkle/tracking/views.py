from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import models
from .models import TrackedCard, ValueSnapshot, CardPricing
from .forms import TrackedCardForm


def tracking_list(request):
    tracked_cards = TrackedCard.objects.all()

    status_filter = request.GET.get('status')
    if status_filter and status_filter in dict(TrackedCard.STATUS_CHOICES):
        tracked_cards = tracked_cards.filter(status=status_filter)

    context = {
        'tracked_cards': tracked_cards,
        'status_choices': TrackedCard.STATUS_CHOICES,
        'current_filter': status_filter or 'all',
        'sold_total': TrackedCard.objects.filter(status='sold').exclude(sold_price__isnull=True).aggregate(total=models.Sum('sold_price'))['total'] or 0,
    }
    return render(request, 'tracking/tracking_list.html', context)


def tracking_detail(request, pk):
    card = get_object_or_404(TrackedCard, pk=pk)
    return render(request, 'tracking/tracking_detail.html', {'card': card})


def tracking_add(request):
    if request.method == 'POST':
        form = TrackedCardForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Now tracking {form.cleaned_data["card_name"]}!')
            return redirect('tracking:list')
    else:
        form = TrackedCardForm()

    return render(request, 'tracking/tracking_form.html', {
        'form': form,
        'action': 'Add',
    })


def tracking_edit(request, pk):
    card = get_object_or_404(TrackedCard, pk=pk)

    if request.method == 'POST':
        form = TrackedCardForm(request.POST, instance=card)
        if form.is_valid():
            form.save()
            messages.success(request, f'Updated {card.card_name}.')
            return redirect('tracking:detail', pk=card.pk)
    else:
        form = TrackedCardForm(instance=card)

    return render(request, 'tracking/tracking_form.html', {
        'form': form,
        'action': 'Edit',
        'card': card,
    })


def tracking_delete(request, pk):
    card = get_object_or_404(TrackedCard, pk=pk)

    if request.method == 'POST':
        card_name = card.card_name
        card.delete()
        messages.success(request, f'Stopped tracking {card_name}.')
        return redirect('tracking:list')

    return render(request, 'tracking/tracking_delete.html', {'card': card})


def market_search(request):
    query = request.GET.get('q', '')
    set_filter = request.GET.get('set', '')
    sort = request.GET.get('sort', 'name')
    grade_filter = request.GET.get('grade', '')

    if query:
        cards_qs = CardPricing.objects.filter(card_name__icontains=query)
    else:
        cards_qs = CardPricing.objects.all()

    if set_filter:
        cards_qs = cards_qs.filter(card_set=set_filter)

    unique_cards = cards_qs.values('card_name', 'card_set').distinct()

    card_list = []
    for card in unique_cards:
        tier = grade_filter if grade_filter else 'ungraded'
        latest = CardPricing.objects.filter(
            card_name=card['card_name'],
            card_set=card['card_set'],
            grade_tier=tier,
        ).order_by('-date_recorded').first()
        card_list.append({
            'card_name': card['card_name'],
            'card_set': card['card_set'],
            'price': latest.price if latest else None,
        })

    if sort == '-name':
        card_list.sort(key=lambda c: c['card_name'], reverse=True)
    elif sort == 'price_low':
        card_list.sort(key=lambda c: c['price'] or 0)
    elif sort == 'price_high':
        card_list.sort(key=lambda c: c['price'] or 0, reverse=True)
    else:
        card_list.sort(key=lambda c: c['card_name'])

    sets = list(CardPricing.objects.values_list('card_set', flat=True).distinct().order_by('card_set'))

    context = {
        'query': query,
        'cards': card_list,
        'sets': sets,
        'current_set': set_filter,
        'current_sort': sort,
        
    }
    return render(request, 'tracking/market_search.html', context)