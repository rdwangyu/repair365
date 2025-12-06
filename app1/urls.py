from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RepairFormViewSet, UserProfileViewSet

router = DefaultRouter()
router.register(r'repair', RepairFormViewSet, basename='repair_form')
router.register(r'user', UserProfileViewSet, basename='user_profile')

urlpatterns = [
    path('api/', include(router.urls)),
]

