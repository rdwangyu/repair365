from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RepairOrderViewSet, UserProfileViewSet

router = DefaultRouter()
router.register(r'repair', RepairOrderViewSet, basename='repair_order')
router.register(r'user', UserProfileViewSet, basename='user_profile')

urlpatterns = [
    path('api/', include(router.urls)),
]

