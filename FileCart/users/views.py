from .serializers import ProfileSerializer
from .permissions import IsOwnerOrAdmin
from django.core.mail import  EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Profile
from .serializers import BalanceTopUpSerializer, BalanceConfirmSerializer

# Профиль текущего пользователя
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_object(self):
        return self.request.user.profile

# Публичный просмотр профилей
class PublicProfileView(generics.RetrieveAPIView):
    queryset = Profile.objects.select_related('user').all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'user__id'
    lookup_url_kwarg = 'pk'

# API для удаления профиля (только админ)
class AdminDeleteProfileView(generics.DestroyAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAdminUser]

# Запрос на пополнение баланса (отправка кода)
class BalanceTopUpView(generics.GenericAPIView):
    """Отправляет код подтверждения на email"""
    serializer_class = BalanceTopUpSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        amount = serializer.validated_data['amount']
        user_profile = request.user.profile

        # Генерируем код и сохраняем сумму пополнения
        user_profile.generate_confirmation_code(amount)

        # Генерируем HTML-шаблон письма
        context = {
            "username": request.user.username,
            "confirmation_code": user_profile.confirmation_code,
            "amount": amount,
            "profile_url": "http://127.0.0.1:8000/api4/profile/"
        }
        html_content = render_to_string("emails/balance_confirmation.html", context)
        text_content = strip_tags(html_content)  # Убираем HTML для текстовой версии

        # Отправка письма
        email_message = EmailMultiAlternatives(
            subject="Код подтверждения пополнения",
            body=text_content,
            from_email="abdugood03@gmail.com",
            to=[email]
        )
        email_message.attach_alternative(html_content, "text/html")
        email_message.send()

        return Response({"message": "Код подтверждения отправлен на email."}, status=status.HTTP_200_OK)

# Подтверждение пополнения баланса
class BalanceConfirmView(generics.GenericAPIView):
    serializer_class = BalanceConfirmSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_profile = request.user.profile
        code = serializer.validated_data['code']

        if user_profile.confirmation_code == code:
            if user_profile.pending_amount is None:
                return Response({"error": "Нет ожидаемой суммы пополнения!"}, status=status.HTTP_400_BAD_REQUEST)

            user_profile.balance += user_profile.pending_amount
            user_profile.confirmation_code = None
            user_profile.pending_amount = None
            user_profile.save()

            return Response({"message": "Баланс успешно пополнен!", "balance": f'{user_profile.balance} сом'}, status=status.HTTP_200_OK)

        return Response({"error": "Неверный код подтверждения!"}, status=status.HTTP_400_BAD_REQUEST)
