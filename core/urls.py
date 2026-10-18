from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('users/', include('users.urls')),
    path('activities/', include('activities.urls')),
    path('notifications/', include('notifications.urls')),
    path('admin-panel/', include('admin_panel.urls')),
    # Accept underscore path too (some links or bookmarks use `admin_panel/`)
    # Redirect the underscored path to the canonical dashed path to avoid
    # registering the same app URLs twice (which causes namespace warnings).
    path('admin_panel/', RedirectView.as_view(pattern_name='admin_panel:dashboard', permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)