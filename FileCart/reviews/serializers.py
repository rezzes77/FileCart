from rest_framework import serializers
from .models import Review,  ProductLike, ReviewLike
from products.models import Product

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['user', 'created_at']
class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

    def get_like_count(self, obj):
        return obj.reactions.filter(reaction=ProductLike.LIKE).count()

    def get_dislike_count(self, obj):
        return obj.reactions.filter(reaction=ProductLike.DISLIKE).count()

class ProductStatsSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'average_rating', 'like_count', 'dislike_count']

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0

    def get_like_count(self, obj):
        return obj.reactions.filter(reaction=ProductLike.LIKE).count()

    def get_dislike_count(self, obj):
        return obj.reactions.filter(reaction=ProductLike.DISLIKE).count()