from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_drf_blog_api'

    def ready(self):
        import django_drf_blog_api.signals
