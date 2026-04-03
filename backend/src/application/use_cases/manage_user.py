from ...domain.ports.output.user_repository_port import UserRepositoryPort
from ...domain.entities.user import User
from ...domain.exceptions.domain_exceptions import ValidationError, DomainError
from ..validators.regex_validators import validate_email, validate_password
from ...infrastructure.security.password_hasher import hash_password, verify_password
from ...infrastructure.security.jwt_handler import create_access_token, create_refresh_token


class ManageUserUseCase:
    def __init__(self, repo: UserRepositoryPort):
        self._repo = repo

    async def register(self, email: str, password: str, display_name: str) -> User:
        if not validate_email(email):
            raise ValidationError("email", "Formato de email inválido")
        if not validate_password(password):
            raise ValidationError(
                "password",
                "Mínimo 8 caracteres, 1 mayúscula y 1 número"
            )
        existing = await self._repo.get_by_email(email)
        if existing:
            raise DomainError(code="EMAIL_TAKEN", message="El email ya está registrado")

        user = User(
            email=email,
            password_hash=hash_password(password),
            display_name=display_name,
        )
        return await self._repo.create(user)

    async def login(self, email: str, password: str) -> dict:
        user = await self._repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise DomainError(code="INVALID_CREDENTIALS", message="Credenciales inválidas")

        access_token = create_access_token({"sub": user.id, "email": user.email})
        refresh_token = create_refresh_token({"sub": user.id})
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user_id": user.id,
        }
