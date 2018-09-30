import hashlib
import os
from wsgiref.util import FileWrapper

from django.conf import settings
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser

from permissions import ActionBasedPermission, IsCreditor
from core.models import Offer, Proposal
from .serializers import OfferSerializer, CreateOfferSerializer


class OfferModelViewSet(ModelViewSet):
    serializer_class = OfferSerializer
    permission_classes = (ActionBasedPermission,)
    action_permissions = {
        IsCreditor: ['create', 'list', 'retrieve'],
        IsAdminUser: [
            'create', 'list', 'retrieve', 'update', 'partial_update', 'destroy'
        ]
    }

    def get_queryset(self):
        user = self.request.user
        return Offer.objects.filter(user=user)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = CreateOfferSerializer(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(
            self.serializer_class(instance).data,
            status=status.HTTP_201_CREATED
        )


@api_view(['GET'])
def download_pdf(request, pk):
    user = request.user
    if user.role == 'partner':
        raise ValidationError("partner can't download proposals")

    offer_ids = Offer.objects.filter(user_id=user.pk).values_list('id', flat=True)
    proposal = Proposal.objects.filter(
        pk=pk,
        offer_id__in=offer_ids,
    ).first()

    if not proposal:
        raise ValidationError("There is no such proposal")

    pdf_name_with_salt = f"proposal{pk}{settings.SECRET_KEY}".encode()
    hashed_pdf_file = hashlib.sha512(pdf_name_with_salt).hexdigest()
    pf = f"{settings.BASE_DIR}/proposals/{hashed_pdf_file}.pdf"

    try:
        wrapper = FileWrapper(open(pf, 'rb'))
        response = HttpResponse(wrapper, content_type='application/force-download')
        response['Content-Disposition'] = 'inline; filename=' + os.path.basename(pf)
        return response
    except Exception as e:
        return Response(
            {'error': 'file does not exist, it was may be deleted'},
            status=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS
        )
