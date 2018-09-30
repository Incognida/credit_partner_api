from django.db import models
from utils import (User, phone_regex,
                   FormException, OfferException, ProposalException,
                   STATUS_CHOICES, LOAN_CHOICES)


class Form(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='forms', verbose_name='partner'
    )
    surname = models.CharField(max_length=150)
    name = models.CharField(max_length=50)
    patronymic = models.CharField(max_length=150)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(validators=[phone_regex], max_length=10)
    passport_number = models.CharField(max_length=25)
    rating = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.user.role != 'partner':
            raise FormException("Form isn't belong to partner!")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"rating = {self.rating}"


class Proposal(models.Model):
    form = models.ForeignKey(
        'core.Form', on_delete=models.CASCADE, related_name='proposals'
    )
    offer = models.ForeignKey(
        'core.Offer', on_delete=models.CASCADE, related_name='proposals'
    )

    status = models.CharField(choices=STATUS_CHOICES, max_length=8, default='new')

    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = (("form", "offer"),)


class Offer(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='offers'
    )

    description = models.CharField(max_length=150)
    loan_type = models.CharField(choices=LOAN_CHOICES, max_length=4, default='cash')
    min_rating = models.PositiveIntegerField(default=0)
    max_rating = models.PositiveIntegerField(default=0)

    rotation_began_at = models.DateTimeField(blank=True, null=True)
    rotation_ended_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.user.role != 'creditor':
            raise OfferException("Offer isn't belong to creditor")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"""
        min_rating = {self.min_rating}, max_rating = {self.max_rating}, 
        loan_type = {self.loan_type}
        """
