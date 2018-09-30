from django.urls import path
from .views import CreateUserView, sign_in, UserView


urlpatterns = [
    path('sign_up/', CreateUserView.as_view(), name='sign_up'),
    path('sign_in/', sign_in, name='sign_in'),
    path('profile/', UserView.as_view(), name='profile'),
]
