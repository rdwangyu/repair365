from django.urls import path, include
from .views import *

urlpatterns = [
    path('customer/updateProfile', updateCustomerProfile),
    path('master/', UserMasterView.as_view())
]

