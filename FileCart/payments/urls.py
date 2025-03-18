from django.urls import path
from . import views

urlpatterns = [
    path('top-up/', views.TopUpBalanceView.as_view(), name='top-up'),
    path('confirm/<int:transaction_id>/', views.ConfirmTopUpView.as_view(), name='confirm-top-up'),
]