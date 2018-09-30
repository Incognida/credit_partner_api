from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FormModelViewSet, SuitableOffersListApiView

router = DefaultRouter()
router.register(r'', FormModelViewSet, base_name='forms')

urlpatterns = [
    path('forms/', include(router.urls), name='forms'),
    path('show_offers/', SuitableOffersListApiView.as_view(), name='show_offers'),
]
