from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

User = get_user_model()


class FormException(Exception):
    pass


class ProposalException(Exception):
    pass


class OfferException(Exception):
    pass


phone_regex = RegexValidator(regex=r'^\d{10}$',
                             message="Номер телефона должен быть в формате "
                                     "9999999999")

STATUS_CHOICES = (
    ('new', 'new'),
    ('sent', 'sent'),
    ('received', 'received'),
    ('approved', 'approved'),
    ('denied', 'denied'),
    ('issued', 'issued')
)
LOAN_CHOICES = (
    ('cash', 'cash'),
    ('home', 'home'),
    ('auto', 'auto')
)
