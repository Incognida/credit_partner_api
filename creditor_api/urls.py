from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OfferModelViewSet, download_pdf

router = DefaultRouter()
router.register(r'', OfferModelViewSet, base_name='offers')

urlpatterns = [
    path('offers/', include(router.urls), name='offers'),
    path('download_pdf/<int:pk>', download_pdf, name='download_pdf'),
]
