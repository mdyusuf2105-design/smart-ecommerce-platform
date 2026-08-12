import jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import ALGORITHM, SECRET_KEY
from app.database.database import get_db
from app.models.user import User

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("type") != "access":
            raise HTTPException(
                status_code=401,
                detail="Access token required"
            )

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    user = db.get(User, int(user_id))

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user


def require_admin(
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return current_user


def require_staff(
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=403,
            detail="Staff access required"
        )

    return current_user


def require_customer(
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "customer":
        raise HTTPException(
            status_code=403,
            detail="Customer access required"
        )

    return current_user