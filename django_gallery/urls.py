"""
URL configuration for django_gallery project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # 웹 페이지 URL
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('artists/', include('artists.urls')),
    path('artworks/', include('artworks.urls')),
    path('management/', include('management.urls')),
    path('exhibitions/', include('exhibitions.urls')),
    
    # API URL
    path('api/v1/', include('accounts.api_urls')),
    path('api/v1/artists/', include('artists.api_urls')),
    path('api/v1/artworks/', include('artworks.api_urls')),
    path('api/v1/exhibitions/', include('exhibitions.api_urls')),
    
    path('api-auth/', include('rest_framework.urls')),
]

# 개발 환경에서 미디어 파일 서빙
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
 