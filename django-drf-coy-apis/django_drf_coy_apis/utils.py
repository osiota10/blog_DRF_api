import random
import string
from django.utils.text import slugify


def random_string_generator(size=4, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_slug_generator(instance, new_slug=None):
    """
    Generates a unique slug for a model instance featuring a slug field.
    """
    if new_slug is not None:
        slug = new_slug
    else:
        title = getattr(instance, 'title', None) or getattr(instance, 'name', None) or getattr(instance, 'job_title', None) or ""
        slug = slugify(title)

    if not slug:
        slug = random_string_generator(size=8)

    Klass = instance.__class__
    qs = Klass.objects.filter(slug=slug)
    if instance.pk:
        qs = qs.exclude(pk=instance.pk)

    if qs.exists():
        new_slug = f"{slug}-{random_string_generator(size=4)}"
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug
