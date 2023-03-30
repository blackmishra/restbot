from django.contrib import admin
from django.urls import path, include
from resy import urls as resy_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('restbot/', include(resy_urls)),
]
