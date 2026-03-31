from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.user import CreateUserSchema, UserResponseSchema, LoginSchema, TokenResponseSchema
from services.user_service import UserService

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: CreateUserSchema,
    db: Session = Depends(get_db)
) -> UserResponseSchema:
    """
    Endpoint para cadastro de novos usuários.
    
    - **nome**: Nome do usuário (3-255 caracteres)
    - **email**: Email único do usuário
    - **senha**: Senha com mínimo de 6 caracteres
    """
    try:
        user = UserService.register_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao registrar usuário"
        )


@router.post("/login", response_model=TokenResponseSchema)
async def login(
    login_data: LoginSchema,
    db: Session = Depends(get_db)
) -> TokenResponseSchema:
    """
    Endpoint para login de usuários.
    
    - **email**: Email do usuário
    - **senha**: Senha do usuário
    
    Retorna um access_token para utilizar no WebSocket
    """
    try:
        token = UserService.login_user(db, login_data)
        return token
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao fazer login"
        )
