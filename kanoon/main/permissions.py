# permissions.py

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff


class IsOwnerOrAdminOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        if request.method in ['POST', 'GET']:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff
