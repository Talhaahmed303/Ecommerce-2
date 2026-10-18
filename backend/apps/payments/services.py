from .models import PaymentTransaction

class MockPaymentException(Exception):
    pass

class MockPaymentGateway:
    """
    Simulated Payment Gateway engine for E-Commerce MVP.
    Never charges real money. Accurately simulates card processing outcomes
    and strictly enforces idempotency.
    """

    SUPPORTED_TOKENS = {
        'tok_success': ('success', 'Payment authorized and settled successfully.'),
        'tok_decline': ('declined', 'Transaction declined by issuing bank: Insufficient funds.'),
        'tok_invalid_cvv': ('declined', 'Transaction declined: Invalid CVV security code.'),
        'tok_expired_card': ('declined', 'Transaction declined: Card is expired.'),
        'tok_gateway_timeout': ('error', 'Gateway timeout: Bank upstream connection error.'),
    }

    @classmethod
    def process_payment(cls, user, amount, payment_token, idempotency_key):
        # 1. Idempotency Check
        existing_tx = PaymentTransaction.objects.filter(idempotency_key=idempotency_key).first()
        if existing_tx:
            return existing_tx

        # 2. Token evaluation
        if payment_token not in cls.SUPPORTED_TOKENS:
            # Default unknown token to decline for security
            outcome_status, message = ('declined', f"Unsupported mock token '{payment_token}'. Use 'tok_success' or 'tok_decline'.")
        else:
            outcome_status, message = cls.SUPPORTED_TOKENS[payment_token]

        # 3. Persist transaction record
        tx = PaymentTransaction.objects.create(
            idempotency_key=idempotency_key,
            user=user,
            amount=amount,
            payment_token=payment_token,
            status=outcome_status,
            gateway_message=message
        )
        return tx
