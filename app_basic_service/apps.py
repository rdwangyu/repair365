from django.apps import AppConfig


class AppBaseServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_basic_service'
