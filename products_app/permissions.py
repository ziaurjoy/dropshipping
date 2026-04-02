from rest_framework import permissions


class IsReadOnlyForRegularUsers(permissions.BasePermission):
    """
    Allows read-only access for unauthenticated users and users with user_type='user'
    Full access for other authenticated users (admin, staff, seller, etc.)
    """

    def has_permission(self, request, view):
        # Allow safe methods (read-only) for everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # For unsafe methods (POST, PUT, PATCH, DELETE), check authentication and user_type
        if not request.user or not request.user.is_authenticated:
            return False

        # If user_type is 'user', deny write operations
        if hasattr(request.user, 'user_type') and request.user.user_type == 'user':
            return False

        # Otherwise (admin, staff, seller, etc.), allow write operations
        return True




def has_write_permission(user):
    """
    RBAC Function: Determines if a user has write permission (POST, PUT, PATCH, DELETE)

    Returns:
        True  -> User can create/update/delete
        False -> User can only read
    """
    if not user or not user.is_authenticated:
        return False

    # Add your logic here based on user_type / role

    # Example 1: Only 'admin' and 'seller' can write
    allowed_roles = ['ADMIN', 'VENDOR', "STAFF"]

    user_type = getattr(user, 'user_type', None) or getattr(user, 'role', None)

    if user_type in allowed_roles:
        return True

    # Regular 'user' or any other type → Read only
    return False


class RBACPermission(permissions.BasePermission):
    """
    Reusable RBAC Permission Class
    - Everyone can READ (GET, HEAD, OPTIONS)
    - Only users with write permission can modify (POST, PUT, PATCH, DELETE)
    """

    def has_permission(self, request, view):
        # Safe methods (Read) - Allowed for everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Unsafe methods (Write) - Check RBAC function
        return has_write_permission(request.user)