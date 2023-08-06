from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import BasePermission


class HasValidRole(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        roles = set(view.roles)
        roles.add(view.base_role)
        access_denied = (
            not user.is_authenticated or (
                not user.is_superuser
                and user.user_roles.filter(role__in=roles).count() == 0
            )
        )
        return not access_denied


class GASAuthMixin:
    authentication_classes = [SessionAuthentication]
    permission_classes = [HasValidRole]
    base_role = 'admins'
    roles = set()
