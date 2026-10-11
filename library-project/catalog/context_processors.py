from django.conf import settings
from django.utils import timezone


def site(request):
    return {
        "SITE_NAME": settings.SITE_NAME,
        "SITE_OWNER": settings.SITE_OWNER,
        "YEAR": timezone.now().year,
    }
