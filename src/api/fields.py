from decimal import Decimal

from rest_framework import serializers


class AmountField(serializers.DecimalField):
    def __init__(self, max_digits=15, decimal_places=2, *args, **kwargs):
        super().__init__(
            max_digits=max_digits,
            decimal_places=decimal_places,
            min_value=Decimal(0),
            *args,
            **kwargs,
        )
