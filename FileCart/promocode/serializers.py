from rest_framework import serializers
from .models import PromoCode

class PromoCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = '__all__'
        read_only_fields = ('current_uses', 'is_active')

class PromoCodeActivateSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=20)