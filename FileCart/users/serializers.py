from rest_framework import serializers
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    balance = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['id', 'username', 'email', 'avatar', 'full_name', 'phone',
                  'bio', 'date_of_birth', 'address', 'gender', 'created_at', 'updated_at', 'balance']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_balance(self, obj):
        """Показывает баланс только владельцу"""
        request = self.context.get('request')
        if request and request.user == obj.user:
            return f"{obj.balance} сом"
        return None  # Баланс не виден другим пользователям

class BalanceTopUpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Сумма должна быть больше 0.")
        if value > 1000000:
            raise serializers.ValidationError("Максимальная сумма пополнения — 1000000 сомов.")
        return value

class BalanceConfirmSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)
