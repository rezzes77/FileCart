from rest_framework.permissions import BasePermission


class IsOwnerOrAdmin(BasePermission):
    """
    Разрешение доступа: только владелец может редактировать, только админ может удалять.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in ['DELETE']:
            return request.user.is_staff  # Удалять может только админ
        return obj.user == request.user  # Редактировать может только владелец
