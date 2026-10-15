from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Provides the 'login' and 'logout' URL names used by base.html and @login_required.
    path('accounts/', include('django.contrib.auth.urls')),
    path('books/', include('library.urls', namespace='library')),
    path('', RedirectView.as_view(pattern_name='library:book-list', permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
