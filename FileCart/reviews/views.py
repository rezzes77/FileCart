from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework.decorators import action
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from products.models import Product
from .models import Review, ProductLike, ReviewLike
from .serializers import ReviewSerializer, ProductStatsSerializer


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(name="product_id", description="ID товара", required=True, type=int)
        ],
        responses={200: ReviewSerializer(many=True)}
    ),
    create=extend_schema(
        request=ReviewSerializer,
        responses={201: ReviewSerializer}
    ),
    destroy=extend_schema(
        responses={204: None}
    )
)
class ReviewViewSet(viewsets.ViewSet):
    """Обработчик отзывов для товаров"""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def list(self, request, product_id=None):
        """ Получить список отзывов для конкретного товара """
        product = get_object_or_404(Product, id=product_id)
        reviews = Review.objects.filter(product=product)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        """ Оставить отзыв на товар """
        product_id = request.data.get("product_id")
        rating = request.data.get("rating")
        text = request.data.get("text", "")

        if not product_id or not rating:
            return Response({"error": "Поля product_id и rating обязательны"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            rating = int(rating)
        except ValueError:
            return Response({"error": "Оценка должна быть числом от 1 до 5"}, status=status.HTTP_400_BAD_REQUEST)

        if not (1 <= rating <= 5):
            return Response({"error": "Оценка должна быть от 1 до 5"}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, id=product_id)

        review, created = Review.objects.get_or_create(
            user=request.user, product=product,
            defaults={"rating": rating, "text": text}
        )

        if not created:
            return Response({"error": "Вы уже оставляли отзыв на этот товар"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        """ Удалить отзыв (только автор) """
        review = get_object_or_404(Review, id=pk)
        if review.user != request.user:
            return Response({"error": "Вы не можете удалить этот отзыв"},
                            status=status.HTTP_403_FORBIDDEN)
        review.delete()
        return Response({"message": "Отзыв удален"}, status=status.HTTP_204_NO_CONTENT)


class ProductReactionViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def react(self, request, pk=None):
        product = get_object_or_404(Product, id=pk)
        reaction = request.data.get('reaction')

        if reaction not in [True, False]:
            return Response({'error': 'Invalid reaction'}, status=status.HTTP_400_BAD_REQUEST)

        obj, created = ProductLike.objects.update_or_create(
            user=request.user,
            product=product,
            defaults={'reaction': reaction}
        )

        return Response({'status': 'reaction updated'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        product = get_object_or_404(Product, id=pk)
        serializer = ProductStatsSerializer(product)
        return Response(serializer.data)


class ReviewReactionViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def react(self, request, pk=None):
        review = get_object_or_404(Review, id=pk)
        reaction = request.data.get('reaction')

        if reaction not in [True, False]:
            return Response({'error': 'Invalid reaction'}, status=status.HTTP_400_BAD_REQUEST)

        obj, created = ReviewLike.objects.update_or_create(
            user=request.user,
            review=review,
            defaults={'reaction': reaction}
        )

        return Response({'status': 'reaction updated'}, status=status.HTTP_200_OK)