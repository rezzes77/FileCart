from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import PromoCodeViewSet, PromoCodeUserViewSet

router = DefaultRouter()
router.register(r'promocodes', PromoCodeViewSet, basename='promocodes')

urlpatterns = [
    path('promocode/activate/', PromoCodeUserViewSet.as_view({'post': 'activate'})),
] + router.urls