from django.core.exceptions import PermissionDenied

from users.models import User


def has_common_user_permission(user: User, raise_exception: bool = False) -> bool:
    """
    Check if user is common active user.
    """
    if user and user.is_authenticated and user.is_active and not user.is_banned:
        return True
    if raise_exception:
        raise PermissionDenied()
    return False


def has_moderator_permissions(user: User, raise_exception: bool = False) -> bool:
    """
    Check if user is moderator.
    """
    if has_common_user_permission(user, raise_exception) and user.is_staff:
        return True
    if raise_exception:
        raise PermissionDenied()
    return False


def has_admin_permission(user: User, raise_exception: bool = False) -> bool:
    """
    Check if user is admin.
    """
    if has_moderator_permissions(user, raise_exception) and user.is_superuser:
        return True
    if raise_exception:
        raise PermissionDenied()
    return False
