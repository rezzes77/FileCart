import random
from django.db import transaction
from .models import Transaction
from users.models import Profile

def generate_confirmation_code():
    return str(random.randint(100000, 999999))

@transaction.atomic
def process_top_up(profile, amount, phone):
    code = generate_confirmation_code()
    # В реальном проекте: отправить код на номер `phone` через SMS
    transaction = Transaction.objects.create(
        profile=profile,
        amount=amount,
        code=code,
        status='pending'
    )
    return transaction