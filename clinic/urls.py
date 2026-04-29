from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('auth/', include('apps.core.auth_urls')),
    path('patients/', include('apps.patients.urls')),
    path('appointments/', include('apps.appointments.urls')),
    path('pharmacy/', include('apps.pharmacy.urls')),
    path('finance/', include('apps.finance.urls')),
    path('staff/', include('apps.staff.urls')),
    path('reports/', include('apps.reports.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
