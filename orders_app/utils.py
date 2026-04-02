
from django.utils import timezone
from django.utils import timezone
import random
import string
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



def generate_tracking_number(self):
        """Generate tracking number based on carrier"""
        if self.carrier.lower() == 'pathao':
            prefix = "PAT"
        elif self.carrier.lower() == 'skyship':
            prefix = "SKY"
        else:
            prefix = "TRK"

        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))
        return f"{prefix}{random_part}"

def generate_tracking_url(self):
    """Generate tracking URL based on carrier"""
    if self.carrier.lower() == 'pathao':
        return f"https://pathao.com/track/{self.tracking_number}"
    elif self.carrier.lower() == 'skyship':
        return f"https://skyship.com/track/{self.tracking_number}"
    else:
        return f"https://example.com/track/{self.tracking_number}"