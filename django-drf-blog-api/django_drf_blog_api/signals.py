import concurrent.futures
from django.db.models.signals import pre_save, post_save
from django.conf import settings
from .utils import unique_slug_generator
from .models import Post, MagazineSeries, SocialPostLog
from .social_posters import (
    get_platform_credentials, FacebookPoster, InstagramPoster, XPoster, LinkedInPoster
)

POSTER_MAP = {
    'facebook': FacebookPoster,
    'instagram': InstagramPoster,
    'twitter': XPoster,
    'linkedin': LinkedInPoster,
}


def slug_generator(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


pre_save.connect(slug_generator, sender=Post)
pre_save.connect(slug_generator, sender=MagazineSeries)


def dispatch_social_posts(post_id: int):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return

    frontend_url = getattr(settings, 'SOCIAL_AUTO_POST', {}).get('FRONTEND_SITE_URL', 'https://yourdomain.com')
    article_url = f"{frontend_url.rstrip('/')}/blog/{post.slug or post.id}"

    for platform_name, poster_cls in POSTER_MAP.items():
        creds = get_platform_credentials(platform_name)
        if not creds.get('enabled'):
            continue

        log = SocialPostLog.objects.create(
            post=post,
            platform=platform_name,
            status='pending'
        )

        poster = poster_cls(creds)
        res = poster.publish(post, article_url)

        if res.get('success'):
            log.status = 'published'
            log.external_post_id = res.get('post_id')
            log.external_post_url = res.get('post_url')
        else:
            log.status = 'failed'
            log.error_message = res.get('error')
        log.save()


def trigger_social_auto_post(sender, instance, created, **kwargs):
    if created:
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)
        executor.submit(dispatch_social_posts, instance.id)


post_save.connect(trigger_social_auto_post, sender=Post)
