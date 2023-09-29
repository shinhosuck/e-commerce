from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from products.views import home_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('products.urls', namespace='products')),
    path('', include('users.urls', namespace='users')),
    path('', include('sellers.urls', namespace='sellers'))
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)