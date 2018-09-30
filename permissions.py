from rest_framework.permissions import AllowAny, BasePermission


class ActionBasedPermission(AllowAny):
    def has_permission(self, request, view):
        for klass, actions in getattr(view, 'action_permissions', {}).items():
            if view.action in actions:
                return klass().has_permission(request, view)
        return False


class IsPartner(BasePermission):
    def has_permission(self, request, view):
        is_partner = request.user and request.user.is_authenticated and request.user.role == 'partner'
        is_admin = request.user.is_staff
        return is_partner or is_admin


class IsCreditor(BasePermission):
    def has_permission(self, request, view):
        is_creditor = request.user and request.user.is_authenticated and request.user.role == 'creditor'
        is_admin = request.user.is_staff
        return is_creditor or is_admin
