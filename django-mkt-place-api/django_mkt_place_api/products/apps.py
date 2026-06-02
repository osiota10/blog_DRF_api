from django.apps import AppConfig

class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_mkt_place_api.products'
    label = 'products'
    verbose_name = 'Marketplace Products'
