from django.contrib.auth.models import AbstractUser
from django.db import models


USER_CHOICES = (
    ('partner', 'partner'),
    ('creditor', 'creditor')
)


class CustomUser(AbstractUser):
    role = models.CharField(choices=USER_CHOICES, max_length=8, blank=True)
