from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from .models import PromoCode, PromoCodeUsage
from .serializers import PromoCodeSerializer, PromoCodeActivateSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class PromoCodeViewSet(viewsets.ModelViewSet):
    queryset = PromoCode.objects.all()
    serializer_class = PromoCodeSerializer
    permission_classes = [permissions.IsAdminUser]



class PromoCodeUserViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'code': openapi.Schema(type=openapi.TYPE_STRING, description="Промокод")
            },
            required=['code']
        )
    )
    @action(detail=False, methods=['post'])
    def activate(self, request):
        serializer = PromoCodeActivateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data['code']
        try:
            promo = PromoCode.objects.get(code=code, is_active=True)
        except PromoCode.DoesNotExist:
            return Response({"error": "Промокод не найден"}, status=status.HTTP_400_BAD_REQUEST)

        # Проверка валидности
        if not promo.is_valid:
            return Response({"error": "Промокод истек или достиг лимита"}, status=status.HTTP_400_BAD_REQUEST)

        if PromoCodeUsage.objects.filter(user=request.user, promo_code=promo).exists():
            return Response({"error": "Вы уже использовали этот промокод"}, status=status.HTTP_400_BAD_REQUEST)

        # Сохраняем в сессии
        request.session['active_promo'] = {
            'code': promo.code,
            'discount_percent': promo.discount_percent
        }

        return Response({
            "success": f"Промокод активирован! Скидка {promo.discount_percent}%",
            "min_order_amount": promo.min_order_amount
        })

    def get_extra_actions(self):
        return [self.activate]
