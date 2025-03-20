from django.urls import path
from .views import UserProfileView, PublicProfileView, AdminDeleteProfileView, BalanceTopUpView, BalanceConfirmView

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user-profile'),  # Просмотр и редактирование профиля
    path('profile/<int:pk>/', PublicProfileView.as_view(), name='public-profile'),  # Публичный профиль
    path('profile/admin/<int:pk>/delete/', AdminDeleteProfileView.as_view(), name='admin-delete-profile'),  # Удаление профиля
    path('profile/top-up/', BalanceTopUpView.as_view(), name='balance-top-up'),  # Запрос кода пополнения
    path('profile/top-up/confirm/', BalanceConfirmView.as_view(), name='balance-confirm'),  # Подтверждение пополнения
]
