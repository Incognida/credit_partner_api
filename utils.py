from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator


def get_model_fields(model_name):
    from core.models import Form, Offer, Proposal
    model = locals()['%s' % model_name]
    form_fields_list = [field.name for field in model._meta.get_fields() if not field.is_relation]


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
