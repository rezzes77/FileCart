from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Cart, CartItem, Order, OrderItem
from django.db.models import F
from products.models import Product
from .serializers import CartSerializer, OrderSerializer
from django_filters.rest_framework import DjangoFilterBackend


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

        return Response(
            {"message": "Товар добавлен в корзину"},
            status=status.HTTP_201_CREATED
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

    def list(self, request):
        """ Получить список заказов текущего пользователя """
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """ Получить детали конкретного заказа """
        order = get_object_or_404(Order, id=pk, user=request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        """ Оформление заказа """
        user = request.user
        cart = get_object_or_404(Cart, user=user)
        cart_items = CartItem.objects.filter(cart=cart)

        if not cart_items.exists():
            return Response({"detail": "Корзина пуста!"}, status=status.HTTP_400_BAD_REQUEST)

        total_price = 0
        order_items = []
        errors = []

        # Оформление заказа в транзакции
        with transaction.atomic():
            for cart_item in cart_items:
                product = cart_item.product
                quantity = cart_item.quantity

                # Проверяем наличие товара
                if product.stock is not None and product.stock < quantity:
                    errors.append(f"Товара '{product.title}' недостаточно в наличии. Доступно: {product.stock}")
                    continue

                # Уменьшаем количество товара на складе
                if product.stock is not None:
                    product.stock -= quantity
                    product.save()

                # Добавляем товар в заказ
                total_price += product.price * quantity
                order_items.append(OrderItem(
                    product=product,
                    quantity=quantity,
                    price=product.price
                ))

            # Если есть ошибки, возвращаем их
            if errors:
                return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

            # Создаем заказ и добавляем товары
            order = Order.objects.create(user=user, total_price=total_price, status='pending')

            for order_item in order_items:
                order_item.order = order
                order_item.save()

            # Очищаем корзину
            cart_items.delete()

            return Response({
                "id": order.id,
                "user": user.id,
                "status": order.status,
                "total_price": total_price,
                "items": [
                    {
                        "product": item.product.title,
                        "quantity": item.quantity,
                        "price": item.price,
                    } for item in order.items.all()
                ]
            }, status=status.HTTP_201_CREATED)

    from django.db import transaction
    from django.db.models import F

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """ Отмена заказа (если он не был оплачен) """
        order = get_object_or_404(Order, id=pk, user=request.user)

        if order.status == "paid":
            return Response(
                {"error": "Нельзя отменить уже оплаченный заказ"},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            # Возвращаем товары на склад
            order_items = order.items.select_related('product')
            for item in order_items:
                product = item.product
                if product.stock is not None:
                    product.stock = F('stock') + item.quantity
                    product.save()

            # Изменяем статус заказа на отмененный
            order.status = "canceled"
            order.save()

            # Удаляем заказ из базы данных
            order.delete()

        return Response(
            {"message": "Заказ отменен"},
            status=status.HTTP_200_OK
        )