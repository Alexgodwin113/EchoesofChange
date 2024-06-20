import stripe
from django.conf import settings

# stripe.api_key = settings.STRIPE_SECRET_KEY

def create_charge(amount, currency='usd', description='Example charge', source=None):
    try:
        charge = stripe.Charge.create(
            amount=amount,
            currency=currency,
            description=description,
            source=source,
        )
        return charge
    except stripe.error.StripeError as e:
        # Handle error
        print(e)
