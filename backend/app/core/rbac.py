from fastapi import Depends, HTTPException, status
from app.api.deps import get_current_user
from app.models.user import User

class RequiresPermission:
    """
    Dependency injector for RBAC.
    Usage: @router.get("/", dependencies=[Depends(RequiresPermission("read:users"))])
    """
    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    async def __call__(self, current_user: User = Depends(get_current_user)):
        # If user has no role, deny access
        if not current_user.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User role not found. Access denied."
            )
            
        # Admin bypass (optional standard practice)
        if current_user.role.name == "Admin":
            return current_user
            
        # Check permissions
        user_permissions = {p.name for p in current_user.role.permissions}
        if self.required_permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {self.required_permission}"
            )
            
        return current_user
