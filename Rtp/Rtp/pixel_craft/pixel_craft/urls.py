"""
URL configuration for pixel_craft project.
"""
from django.contrib import admin
from django.urls import path, include

# Media file imports
from django.conf import settings        
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Home.urls')),
    path('Accounts/', include('Accounts.urls')),
    path('build/', include('pc_build.urls')),
    path('chatbot/', include('Ai_Assest.urls')),
    path('Vendors/', include('Vendors.urls')),
    path('build/', include('builder.urls')),
]

# This MUST be at the very bottom, outside of the urlpatterns list above
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)