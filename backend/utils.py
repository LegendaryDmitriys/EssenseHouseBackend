from backend.models import PurchasedHouse
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict

def get_period_dates(period):
    today = timezone.now().date()
    if period == '1m':
        start_date = today - timedelta(days=30)
    elif period == '3m':
        start_date = today - timedelta(days=90)
    elif period == '6m':
        start_date = today - timedelta(days=180)
    elif period == '1y':
        start_date = today - timedelta(days=365)
    else:
        start_date = today - timedelta(days=180)
    return start_date, today


def get_projects_data(start_date):
    purchases = (
        PurchasedHouse.objects
        .filter(purchase_date__gte=start_date)
        .select_related('house')
    )

    monthly_data = defaultdict(lambda: {'active': 0, 'completed': 0})

    for p in purchases:
        month = p.purchase_date.strftime('%b')
        key = month
        if p.construction_status == 'completed':
            monthly_data[key]['completed'] += 1
        else:
            monthly_data[key]['active'] += 1

    result = [
        {'name': k, 'active': v['active'], 'completed': v['completed']}
        for k, v in sorted(monthly_data.items())
    ]

    return result


def get_budget_data(start_date):
    purchases = (
        PurchasedHouse.objects
        .filter(purchase_date__gte=start_date)
        .select_related('house')
    )

    monthly_plan = defaultdict(float)
    monthly_actual = defaultdict(float)

    for p in purchases:
        month = p.purchase_date.strftime('%b')
        monthly_plan[month] += round(float(p.house.price) / 1_000_000, 2)
        actual_price = p.house.new_price or p.house.price
        monthly_actual[month] += round(float(actual_price) / 1_000_000, 2)

    result = [
        {'name': m, 'plan': monthly_plan[m], 'actual': monthly_actual[m]}
        for m in sorted(monthly_plan.keys())
    ]

    return result