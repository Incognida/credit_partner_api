from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView

from creditor_api.serializers import OfferSerializer
from permissions import ActionBasedPermission, IsPartner, IsCreditor
from core.models import Form, Offer, Proposal
from .serializers import CreateFormSerializer, FormSerializer, ProposalSerializer, CreateProposalSerializer


class FormModelViewSet(ModelViewSet):
    """
    ---
        CREATE:
        Create form by partner
        {
            "surname": "Rakhimbabin",
            "name": "Zaur",
            "patronymic": "Bakhytovic",
            "date_of_birth": "05-08-1994",
            "phone_number": "9994958508",
            "passport_number": "123456"
        }
    ---
    """
    serializer_class = FormSerializer

    permission_classes = (ActionBasedPermission,)
    action_permissions = {
        IsPartner: ['create', 'list', 'retrieve'],
        IsAdminUser: [
            'create', 'list', 'retrieve', 'update', 'partial_update', 'destroy'
        ]
    }

    def get_queryset(self):
        user = self.request.user
        return Form.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        serializer = CreateFormSerializer(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(
            self.serializer_class(instance).data,
            status=status.HTTP_201_CREATED
        )


class SuitableOffersListApiView(ListAPIView):
    serializer_class = OfferSerializer

    permission_classes = (IsPartner,)

    def get_queryset(self):
        return self.get_suitable_offers()

    def get_suitable_offers(self):
        """
        Get suitable offers depending on all forms of partner

        another query:
        SELECT public.core_offer.id FROM public.core_offer
        INNER JOIN public.core_form
        ON min_rating < rating AND rating < max_rating
        WHERE user_id = %s
        """
        raw_offer_ids = Offer.objects.raw("""
            SELECT id FROM public.core_offer 
            WHERE EXISTS 
                (SELECT 1 FROM public.core_form
                 WHERE rating BETWEEN 
                 min_rating AND max_rating AND user_id = %s)
            """.strip(),
            [self.request.user.pk]
        )
        suitable_offer_ids = set()
        for raw_offer in raw_offer_ids:
            suitable_offer_ids.add(raw_offer.pk)
        return Offer.objects.filter(pk__in=suitable_offer_ids)


class ProposalModelViewSet(ModelViewSet):
    """
    ---
        CREATE:
        Send all partner's forms that satisfy requirements of all offers
        {
            "send_to_all": true
        }

        Send partner's form if it satisfy requirements of offer
        {
            "form_id": 3,
            "offer_id": 1
        }

        PATCH:
        Set status of proposal by creditor
        {
            "status": "received"
        }
    ---
    """
    serializer_class = ProposalSerializer

    permission_classes = (ActionBasedPermission,)
    action_permissions = {
        IsPartner: ['create'],
        IsAuthenticated: ['list', 'retrieve'],
        IsCreditor: ['partial_update'],
        IsAdminUser: [
            'create', 'list', 'retrieve', 'update', 'partial_update', 'destroy'
        ]
    }

    def get_queryset(self):
        user = self.request.user
        if user.role == 'partner':
            user_id = user.pk
            user_forms = Form.objects.filter(user_id=user_id)
            form_ids = user_forms.values_list('id', flat=True)
            proposals = Proposal.objects.filter(form_id__in=form_ids)
        elif user.role == 'creditor':
            offer_ids = Offer.objects.filter(user_id=user.pk).values_list('id', flat=True)
            proposals = Proposal.objects.filter(
                offer_id__in=offer_ids, status='new'
            )
        else:
            proposals = Proposal.objects.all()
        return proposals

    def create(self, request, *args, **kwargs):
        serializer = CreateProposalSerializer(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        if not instance:
            return Response(
                {'status': 'all matching proposals were successfully created'},
                status=status.HTTP_201_CREATED
            )
        return Response(
            self.serializer_class(instance).data,
            status=status.HTTP_201_CREATED
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        prop_status = request.data.get('status')
        if prop_status not in ('sent', 'received', 'approved', 'denied', 'issued'):
            raise ValidationError("not valid status")
        instance.status = prop_status
        instance.save()
        return Response(
            self.serializer_class(instance).data,
            status=status.HTTP_202_ACCEPTED
        )
