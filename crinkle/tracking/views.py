from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import TrackedCard
from .forms import TrackedCardForm
from .models import TrackedCard, ValueSnapshot


def tracking_list(request):
    tracked_cards = TrackedCard.objects.all()

    status_filter = request.GET.get('status')
    if status_filter and status_filter in dict(TrackedCard.STATUS_CHOICES):
        tracked_cards = tracked_cards.filter(status=status_filter)

    snapshots = ValueSnapshot.objects.all()
    chart_dates = [s.date.strftime('%b %d') for s in snapshots]
    chart_values = [float(s.total_value) for s in snapshots]

    context = {
        'tracked_cards': tracked_cards,
        'status_choices': TrackedCard.STATUS_CHOICES,
        'current_filter': status_filter or 'all',
        'chart_dates': chart_dates,
        'chart_values': chart_values,
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

def collection_value_data(request):
    from django.http import JsonResponse
    snapshots = ValueSnapshot.objects.all()
    data = {
        'dates': [s.date.strftime('%b %d') for s in snapshots],
        'values': [float(s.total_value) for s in snapshots],
    }
    return JsonResponse(data)