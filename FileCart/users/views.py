from rest_framework import generics, permissions
from .models import Profile
from .serializers import ProfileSerializer
from .permissions import IsOwnerOrAdmin


# API для работы с профилем текущего пользователя
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_object(self):
        return self.request.user.profile


# Публичный просмотр профилей
class PublicProfileView(generics.RetrieveAPIView):
    queryset = Profile.objects.select_related('user').all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'user__id'
    lookup_url_kwarg = 'pk'


# API для удаления профиля (только для администратора)
class AdminDeleteProfileView(generics.DestroyAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAdminUser]
