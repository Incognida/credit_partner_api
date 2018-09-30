"""task URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework_swagger.views import get_swagger_view
from partner_api.views import ProposalModelViewSet

schema_view = get_swagger_view(title='Task API')

other_router = DefaultRouter()
other_router.register(r'', ProposalModelViewSet, base_name='proposals')

urlpatterns = [
    path('', include('accounts.urls')),
    path('admin/', admin.site.urls),
    path('partner_api/', include('partner_api.urls')),
    path('creditor_api/', include('creditor_api.urls')),
    path('proposals/', include(other_router.urls), name='proposals'),
]

if settings.DEBUG:
    urlpatterns += [
        path('docs/', schema_view, name='docs')
    ]
