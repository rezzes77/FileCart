from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from orders.models import OrderItem

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'price', 'user', 'created_at']
    search_fields = ['title', 'description']

    def get_queryset(self):
        """Все пользователи видят все продукты"""
        queryset = Product.objects.all()

        # Фильтры
        is_expensive = self.request.query_params.get('is_expensive', None)
        category_filter = self.request.query_params.get('category')
        price_min = self.request.query_params.get('price_min')
        price_max = self.request.query_params.get('price_max')
        user_filter = self.request.query_params.get('user')
        created_at_filter = self.request.query_params.get('created_at')

        if category_filter:
            queryset = queryset.filter(category_id=category_filter)

        if price_min:
            queryset = queryset.filter(price__gte=price_min)

        if price_max:
            queryset = queryset.filter(price__lte=price_max)

        if is_expensive is not None:
            if is_expensive.lower() == 'true':
                queryset = queryset.filter(price__gte=1000)
            elif is_expensive.lower() == 'false':
                queryset = queryset.filter(price__lt=1000)

        if user_filter:
            queryset = queryset.filter(user_id=user_filter)

        if created_at_filter:
            queryset = queryset.filter(created_at__date=created_at_filter)

        return queryset

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        product = self.get_object()
        user = request.user

        # Проверка оплаченных заказов с этим товаром
        is_purchased = OrderItem.objects.filter(
            order__user=user,
            order__status='paid',
            product=product
        ).exists()

        if not is_purchased:
            return Response(
                {"error": "Товар не оплачен. Для доступа к файлу необходимо оплатить заказ."},
                status=status.HTTP_403_FORBIDDEN
            )

        if not product.file:
            return Response(
                {"error": "Файл товара не найден"},
                status=status.HTTP_404_NOT_FOUND
            )

        return FileResponse(
            product.file.open(),
            as_attachment=True,
            filename=product.file.name.split('/')[-1]
        )
    def perform_create(self, serializer):
        """При создании продукта автоматически назначать владельца"""
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        """Изменять продукт может только его создатель или администратор"""
        product = self.get_object()

        if product.user != request.user and not request.user.is_staff:
            return Response({"error": "Вы не можете изменить этот продукт"},
                            status=status.HTTP_403_FORBIDDEN)

        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """Обновлять продукт (PATCH) может только его создатель или администратор"""
        product = self.get_object()

        if product.user != request.user and not request.user.is_staff:
            return Response({"error": "Вы не можете обновить этот продукт"},
                            status=status.HTTP_403_FORBIDDEN)

        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, pk=None):
        """Удалять продукт может только его создатель или администратор"""
        product = get_object_or_404(Product, id=pk)

        if product.user != request.user and not request.user.is_staff:
            return Response({"error": "Вы не можете удалить этот продукт"},
                            status=status.HTTP_403_FORBIDDEN)

        product.delete()
        return Response({"message": "Продукт удален"}, status=status.HTTP_204_NO_CONTENT)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    search_fields = ['name']

    def get_queryset(self):
        queryset = Category.objects.all()
        search_name = self.request.query_params.get('name', None)
        if search_name:
            queryset = queryset.filter(name__icontains=search_name)
        return queryset

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return super().get_permissions()