from django.db.models.signals import pre_save
from .utils import unique_slug_generator
from .models import Service, Product, Event


def slug_generator(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


pre_save.connect(slug_generator, sender=Service)
pre_save.connect(slug_generator, sender=Product)
pre_save.connect(slug_generator, sender=Event)
