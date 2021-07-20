from rest_framework.exceptions import ValidationError


def validate_min_amount_of_items_in_orders(value):
    if value < 1:
        raise ValidationError('Minimal amount of items of current type in order must be not less then 1.')
