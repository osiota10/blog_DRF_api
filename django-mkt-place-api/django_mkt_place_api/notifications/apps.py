from django.apps import AppConfig

class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_mkt_place_api.notifications'
    label = 'notifications'
    verbose_name = 'Marketplace Notifications'
