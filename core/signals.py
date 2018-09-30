from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Proposal
from .tasks import make_pdf


@receiver(post_save, sender=Proposal)
def my_model_post_save(sender, instance, **kwargs):
    form = instance.form
    offer = instance.offer
    pk = instance.pk
    form_dict = form.__dict__
    offer_dict = offer.__dict__
    del form_dict['_state']
    del offer_dict['_state']
    transaction.on_commit(lambda: make_pdf.apply_async(args=(form_dict, offer_dict, pk)))
