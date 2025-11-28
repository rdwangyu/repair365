from django.urls import path
from .views import UserCreateView

urlpatterns = [
    path('api/users/', UserCreateView.as_view(), name='user-create'),
]
