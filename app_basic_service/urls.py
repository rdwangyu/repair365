from django.urls import path, include
from .views import *

urlpatterns = [
    path('customer/', UserCustomerView.as_view()),
    path('master/', UserMasterView.as_view()),
    path('order/', RepairOrderView.as_view()),
]

