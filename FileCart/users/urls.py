from django.urls import path
from .views import UserProfileView, PublicProfileView, AdminDeleteProfileView

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user-profile'),  # Просмотр и редактирование своего профиля
    path('profile/<int:pk>/', PublicProfileView.as_view(), name='public-profile'),  # Публичный профиль
    path('profile/admin/<int:pk>/delete/', AdminDeleteProfileView.as_view(), name='admin-delete-profile'),
    # Удаление профиля
]
