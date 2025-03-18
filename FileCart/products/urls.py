from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'categories',CategoryViewSet,basename='categories')
router.register(r'products',ProductViewSet,basename='products')

urlpatterns = [
    path('',include(router.urls))
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
