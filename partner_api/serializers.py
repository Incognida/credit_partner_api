from datetime import date

from django.db import connection, IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from accounts.serializers import UserSerializer
from core.models import Form, Proposal, Offer
from core.tasks import make_pdf


class FormSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Form
        fields = '__all__'


class ProposalSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Proposal
        fields = '__all__'


class CreateFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Form
        exclude = ('user', 'created_at', 'updated_at')

    date_of_birth = serializers.DateField(input_formats=['%Y-%m-%d'])

    def create(self, validated_data):
        request = self.context.get('request')
        if not request:
            raise ValidationError("No 'request' in context")
        if not hasattr(request, 'user'):
            raise ValidationError("No 'user' in 'request'")
        validated_data['user'] = request.user
        return Form.objects.create(**validated_data)


class CreateProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        exclude = ('status', 'created_at', 'sent_at', 'form', 'offer')

    send_to_all = serializers.BooleanField(required=False)
    form_id = serializers.IntegerField(min_value=1, required=False)
    offer_id = serializers.IntegerField(min_value=1, required=False)

    def create(self, validated_data):
        request = self.context.get('request')
        if not request:
            raise ValidationError("No 'request' in context")
        if not hasattr(request, 'user'):
            raise ValidationError("No 'user' in 'request'")

        send_to_all = validated_data.get('send_to_all')
        form_id = validated_data.get('form_id')
        offer_id = validated_data.get('offer_id')

        if not (send_to_all or (form_id and offer_id)):
            raise ValidationError("You have to send your proposal to any appropriate creditor")

        if send_to_all:
            self.create_matching_proposals()
            return False

        min_max_rating = Offer.objects.filter(
            pk=offer_id,
        ).values_list('min_rating', 'max_rating').first()

        if not min_max_rating:
            raise ValidationError("There is no such offer")

        form_rating = Form.objects.filter(pk=form_id).values_list('rating', flat=True).first()
        if not form_rating:
            raise ValidationError("There is no such form")
        if form_rating not in range(min_max_rating[0], min_max_rating[1]):
            raise ValidationError("Form rating does not match offer's rating")

        try:
            proposal = Proposal.objects.create(form_id=form_id, offer_id=offer_id)
        except IntegrityError as e:
            if 'unique constraint' in getattr(e, 'message', None):
                raise ValidationError("This proposal is already exists")
            raise ValidationError("Something went wrong")

        return proposal

    def create_matching_proposals(self):
        """
        Creates all proposals that match partner's forms and offers, that doesn't already exists
        """
        user_id = self.context['request'].user.pk

        query = """
        INSERT INTO public.core_proposal (form_id, offer_id, status, created_at) 
        SELECT public.core_form.id, public.core_offer.id, 'new', %s 
        FROM public.core_form INNER JOIN public.core_offer 
        ON  public.core_offer.min_rating <= public.core_form.rating 
            AND public.core_form.rating<= public.core_offer.max_rating 
            AND NOT EXISTS 
            (SELECT 1 FROM public.core_proposal WHERE public.core_form.id = form_id AND public.core_offer.id = offer_id)
        WHERE public.core_form.user_id=%s
        RETURNING form_id, offer_id, id
        """.strip()

        with connection.cursor() as cursor:
            cursor.execute(
                query,
                [date.today().strftime('%Y-%m-%d'), user_id]
            )
            rows = cursor.fetchall()
        if not rows:
            return None

        proposal_ids = []
        for row in rows:
            proposal_ids.append(row[2])

        proposals = Proposal.objects.filter(pk__in=proposal_ids)
        items = []
        for proposal in proposals:
            form = proposal.form
            offer = proposal.offer
            form_dict = form.__dict__
            offer_dict = offer.__dict__
            del form_dict['_state']
            del offer_dict['_state']
            items.append((form_dict, offer_dict, proposal.pk))

        for item in items:
            make_pdf.apply_async(
                args=(
                    item[0], item[1], item[2]
                )
            )
