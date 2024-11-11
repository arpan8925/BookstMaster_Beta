from django.contrib import admin

from django.urls import path, include

from django.conf import settings

from django.conf.urls.static import static



urlpatterns = [

    path('admin/', admin.site.urls),

    path('managerdashboard/', include('managerdashboard.urls')),

    path('', include('frontend.urls')),

    path('auth/', include('authentication.urls')),

    path('dashboard/', include('user_dashboard.urls')),

    path('manager/', include('managerdashboard.urls', namespace='managerdashboard')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


