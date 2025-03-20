from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """ Только админы могут управлять промокодами """

    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsAuthenticated(permissions.BasePermission):
    """ Проверка, аутентифицирован ли пользователь """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
