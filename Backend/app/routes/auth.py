from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.core.database import get_db
from app.core.security import (
    hash_password,
    create_access_token,
)
from app.models.User import User
from app.schemas.auth import RegisterSchema, LoginSchema, TokenSchema
from app.services.authService import authenticate_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register", response_model=TokenSchema, status_code=status.HTTP_201_CREATED
)
def register(data: RegisterSchema, db: Session = Depends(get_db)):
    # ✅ At least one identifier required
    if not data.email and not data.mobile_number:
        raise HTTPException(
            status_code=400,
            detail="Email or mobile number is required",
        )

    # ✅ Check existing user by email or mobile
    existing_user = (
        db.query(User)
        .filter(
            or_(
                User.email == data.email if data.email else False,
                (
                    User.mobile_number == data.mobile_number
                    if data.mobile_number
                    else False
                ),
            )
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User already exists with this email or mobile number",
        )

    # ✅ Create user
    user = User(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        mobile_number=data.mobile_number,
        hashed_password=hash_password(data.password),
        role_id=data.role_id or 5,
        date_of_birth=data.date_of_birth,
        gender=data.gender,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # ✅ Create JWT token
    token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role.role_name if user.role else None,
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@router.post("/login", response_model=TokenSchema)
def login(data: LoginSchema, db: Session = Depends(get_db)):
    user = authenticate_user(
        db=db,
        email=data.email,
        mobile=data.mobile_number,
        password=data.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token(data={"sub": str(user.id), "role": user.role.role_name})

    return {
        "access_token": token,
        "token_type": "bearer",
    }
