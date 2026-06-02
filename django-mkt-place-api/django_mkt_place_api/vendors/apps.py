from django.apps import AppConfig

class VendorsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_mkt_place_api.vendors'
    label = 'vendors'
    verbose_name = 'Marketplace Vendors'
