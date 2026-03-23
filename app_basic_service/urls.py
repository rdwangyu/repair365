from django.urls import path, include
from .views import *

urlpatterns = [
    path('customer/', UserCustomerView.as_view()),
    path('master/', UserMasterView.as_view()),
    path('customer/order/', RepairOrderOfCustomerView.as_view()),
    path('customer/order/<int:pk>/', RepairOrderOfCustomerView.as_view()),
]

