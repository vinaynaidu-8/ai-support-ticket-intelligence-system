from fastapi import Depends, HTTPException

from app.models.user import User
from app.security.auth import get_current_user


def require_role(required_role: str):
    def role_checker(
        current_user: User = Depends(get_current_user),
    ):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to perform this action",
            )

        return current_user

    return role_checker


def require_roles(*required_roles: str):
    def role_checker(
        current_user: User = Depends(get_current_user),
    ):
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to perform this action",
            )

        return current_user

    return role_checker