from django.urls import path
from .views import ReviewViewSet,ProductReactionViewSet, ReviewReactionViewSet

urlpatterns = [
    path('product/<int:product_id>/reviews/', ReviewViewSet.as_view({'get': 'list'}), name='product-reviews'),
    path('reviews/create/', ReviewViewSet.as_view({'post': 'create'}), name='create-review'),
    path('reviews/<int:pk>/delete/', ReviewViewSet.as_view({'delete': 'destroy'}), name='delete-review'),
    path('products/<int:pk>/react/', ProductReactionViewSet.as_view({'post': 'react'}), name='product-react'),
    path('products/<int:pk>/stats/', ProductReactionViewSet.as_view({'get': 'stats'}), name='product-stats'),

    # Review reactions
    path('reviews/<int:pk>/react/', ReviewReactionViewSet.as_view({'post': 'react'}), name='review-react')
]
