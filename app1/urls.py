from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RepairFormViewSet

router = DefaultRouter()
router.register(r'repair', RepairFormViewSet, basename='repair-form')

urlpatterns = [
    path('api/', include(router.urls)),
]

