from django.utils import timezone
from . import models

def generate_order_number(instance):
    today = timezone.now().strftime('%Y%m%d')

    last_order = models.Order.objects.filter(order_number__contains=today).order_by('-id').first()

    if last_order:
        last_sequence = int(last_order.order_number.split('-')[-1])
        new_sequence = last_sequence + 1
    else:
        new_sequence = 1

    return f"ORD-{today}-{new_sequence:06d}"