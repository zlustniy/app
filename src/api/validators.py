from django.utils.translation import gettext
from rest_framework.validators import ValidationError


def is_digit(val):
    if not val.isdigit():
        raise ValidationError(gettext('Значение поля может состоять только из цифр'))
