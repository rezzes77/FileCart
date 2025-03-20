from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Cart, CartItem, Order, OrderItem
from users.models import Profile  # Импорт профиля для работы с балансом
from products.models import Product
from .serializers import CartSerializer, OrderSerializer, OrderHistorySerializer
from django_filters.rest_framework import DjangoFilterBackend
from promocode.models import PromoCode, PromoCodeUsage

class CartViewSet(viewsets.ViewSet):
    """ Обработчик для управления корзиной """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user']
    search_fields = ['items__product__title']

    def list(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'product_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID товара"),
                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description="Количество", default=1),
            },
            required=['product_id']
        )
    )
    @action(detail=False, methods=["post"])
    def add(self, request):
        """ Добавить товар в корзину """
        cart, _ = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity", 1)

        product = get_object_or_404(Product, id=product_id)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            cart_item.quantity += int(quantity)
        cart_item.save()

        return Response({"message": "Товар добавлен в корзину"}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'product_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID товара"),
            },
            required=['product_id']
        )
    )
    @action(detail=False, methods=["post"])
    def remove(self, request):
        """ Удалить товар из корзины """
        cart = get_object_or_404(Cart, user=request.user)
        product_id = request.data.get("product_id")
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)

        cart_item.delete()

        return Response({"message": "Товар удален из корзины"}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["post"])
    def clear(self, request):
        """ Очистить корзину """
        cart = get_object_or_404(Cart, user=request.user)
        cart.items.all().delete()

        return Response({"message": "Корзина очищена"}, status=status.HTTP_204_NO_CONTENT)



class OrderViewSet(viewsets.ViewSet):
    """ Обработчик для управления заказами """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'total_price', 'created_at']
    search_fields = ['items__product__title', 'user__username']

    def retrieve(self, request, pk=None):
        """ Получить детали конкретного заказа """
        order = get_object_or_404(Order, id=pk, user=request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def list(self, request):
        """ Получить список заказов текущего пользователя """
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def history(self, request):
        """ История покупок текущего пользователя """
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        serializer = OrderHistorySerializer(orders, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'promo_code': openapi.Schema(type=openapi.TYPE_STRING, description="Промокод (необязательно)"),
            }
        )
    )
    @action(detail=False, methods=['post'])
    def checkout(self, request):
        """ Оформление заказа с учетом промокодов """
        user = request.user
        profile = get_object_or_404(Profile, user=user)
        cart = get_object_or_404(Cart, user=user)
        cart_items = CartItem.objects.filter(cart=cart)

        if not cart_items.exists():
            return Response({"detail": "Корзина пуста!"}, status=status.HTTP_400_BAD_REQUEST)

        # Получение активного промокода
        active_promo = request.session.get('active_promo')
        promo_code = None
        discount_percent = 0

        if active_promo:
            try:
                promo_code = PromoCode.objects.get(
                    code=active_promo['code'],
                    is_active=True
                )
                discount_percent = promo_code.discount_percent
            except PromoCode.DoesNotExist:
                return Response({"error": "Недействительный промокод"}, status=400)

        total_price = 0
        order_items = []
        errors = []

        with transaction.atomic():
            # Расчет суммы и проверка товаров
            for cart_item in cart_items:
                product = cart_item.product
                quantity = cart_item.quantity

                if product.stock is not None and product.stock < quantity:
                    errors.append(f"Недостаточно '{product.title}'. Доступно: {product.stock}")
                    continue

                if product.stock is not None:
                    product.stock -= quantity
                    product.save()

                item_price = product.price * quantity
                total_price += item_price
                order_items.append(OrderItem(
                    product=product,
                    quantity=quantity,
                    price=product.price
                ))

            if errors:
                return Response({"errors": errors}, status=400)

            # Применение промокода
            final_price = total_price
            if promo_code:
                # Проверка минимальной суммы
                if total_price < promo_code.min_order_amount:
                    return Response({
                        "error": f"Минимальная сумма для промокода: {promo_code.min_order_amount} сом"
                    }, status=400)

                # Проверка доступности промокода
                if not promo_code.is_valid:
                    return Response({"error": "Промокод более не действителен"}, status=400)

                # Расчет скидки
                discount = total_price * discount_percent / 100
                final_price = total_price - discount

            # Проверка баланса
            if profile.balance < final_price:
                return Response({"error": "Недостаточно средств на балансе"}, status=400)

            # Списание средств
            profile.balance -= final_price
            profile.save()

            # Создание заказа
            order = Order.objects.create(
                user=user,
                total_price=final_price,
                status='paid'
            )

            # Создание OrderItem
            for order_item in order_items:
                order_item.order = order
                order_item.save()

            # Обновление промокода
            if promo_code:
                promo_code.current_uses += 1
                if promo_code.current_uses >= promo_code.max_uses:
                    promo_code.is_active = False
                promo_code.save()
                PromoCodeUsage.objects.create(user=user, promo_code=promo_code)
                del request.session['active_promo']

            # Очистка корзины
            cart_items.delete()

            return Response({
                "id": order.id,
                "user": user.id,
                "status": order.status,
                "total_price": f"{final_price} сом",
                "discount": f"{discount} сом" if promo_code else "0 сом",
                "balance_after": f"{profile.balance} сом",
                "items": [
                    {
                        "product": item.product.title,
                        "quantity": item.quantity,
                        "price": item.price,
                    } for item in order.items.all()
                ]
            }, status=status.HTTP_201_CREATED)
