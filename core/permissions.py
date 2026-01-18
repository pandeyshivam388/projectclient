from rest_framework import permissions


class IsClient(permissions.BasePermission):
    """Permission to check if user is a client"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        try:
            return request.user.profile.role == 'client'
        except:
            return False


class IsLawyer(permissions.BasePermission):
    """Permission to check if user is a lawyer"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        try:
            return request.user.profile.role == 'lawyer'
        except:
            return False


class IsClientOrReadOnly(permissions.BasePermission):
    """Permission for clients to create/edit only their own cases"""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.client == request.user


class IsLawyerOrReadOnly(permissions.BasePermission):
    """Permission for lawyers to approve/reject cases"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        try:
            return request.user.profile.role == 'lawyer'
        except:
            return False
