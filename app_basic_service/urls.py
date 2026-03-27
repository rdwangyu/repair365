from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from .views import *

urlpatterns = [
    path('customer/', UserCustomerView.as_view()),
    path('master/', UserMasterView.as_view()),
    path('customer/order/', RepairOrderOfCustomerView.as_view()),
    path('customer/order/<int:pk>/', RepairOrderOfCustomerView.as_view()),
    path('master/order/', RepairOrderOfMasterView.as_view()),
    path('master/order/<int:pk>/', RepairOrderOfMasterView.as_view()),
    path('upload/', UploadImageView.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
