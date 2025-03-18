from rest_framework import serializers
from .models import Transaction
from .services import process_top_up


class TopUpSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    phone = serializers.CharField(max_length=20)

    def create(self, validated_data):
        profile = self.context['request'].user.profile
        amount = validated_data['amount']
        phone = validated_data['phone']
        return process_top_up(profile, amount, phone)

class ConfirmTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['code']