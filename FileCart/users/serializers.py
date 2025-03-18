from rest_framework import serializers
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Profile
        fields = [
            'id', 'username', 'email', 'avatar', 'full_name', 'phone',
            'bio', 'date_of_birth', 'address', 'gender', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'avatar': {'required': False},  # Аватар необязателен
        }
