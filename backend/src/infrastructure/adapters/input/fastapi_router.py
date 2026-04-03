import csv
import io
import json

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ....application.dtos.calculation_request import CalculationRequest
from ....application.dtos.calculation_response import CalculationResponse
from ....application.use_cases.evaluate_expression import EvaluateExpressionUseCase
from ....application.use_cases.manage_history import ManageHistoryUseCase
from ....application.use_cases.manage_favorite_conversions import ManageFavoriteConversionsUseCase
from ....application.use_cases.manage_preferences import ManagePreferencesUseCase
from ....application.use_cases.manage_profile import ManageProfileUseCase
from ....application.use_cases.manage_session import ManageSessionUseCase
from ....application.use_cases.manage_user import ManageUserUseCase
from ....domain.exceptions.domain_exceptions import DomainError
from ...persistence.database import get_db
from ...adapters.output.postgres_history_repo import PostgresHistoryRepo
from ...adapters.output.postgres_preferences_repo import PostgresPreferencesRepo
from ...adapters.output.postgres_favorite_conversion_repo import PostgresFavoriteConversionRepo
from ...adapters.output.postgres_profile_repo import PostgresProfileRepo
from ...adapters.output.postgres_session_repo import PostgresSessionRepo
from ...adapters.output.postgres_sync_repo import PostgresAuditRepo
from ...adapters.output.postgres_user_repo import PostgresUserRepo
from ...adapters.input.math_engine_adapter import MpMathCalculationEngine
from .auth_middleware import get_current_user

router = APIRouter(prefix="/api/v1")

# ── Auth ─────────────────────────────────────────────────────────────────────

@router.post("/auth/register", status_code=201)
async def register(
    email: str,
    password: str,
    display_name: str,
    db: AsyncSession = Depends(get_db),
):
    repo = PostgresUserRepo(db)
    uc = ManageUserUseCase(repo)
    try:
        user = await uc.register(email, password, display_name)
        await PostgresAuditRepo(db).log_action(user.id, "user", user.id, "CREATE")
        return {"id": user.id, "email": user.email, "display_name": user.display_name}
    except DomainError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())


@router.post("/auth/login")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    repo = PostgresUserRepo(db)
    uc = ManageUserUseCase(repo)
    try:
        tokens = await uc.login(form_data.username, form_data.password)
        # Registrar sesión activa (RNF-SEC005 / doc §3.4)
        browser_agent = request.headers.get("User-Agent", "unknown")[:255]
        session_uc = ManageSessionUseCase(PostgresSessionRepo(db))
        await session_uc.register(
            user_id=tokens["user_id"],
            token=tokens["access_token"],
            browser_agent=browser_agent,
        )
        # No exponer user_id en la respuesta pública
        return {k: v for k, v in tokens.items() if k != "user_id"}
    except DomainError as e:
        raise HTTPException(status_code=401, detail=e.to_dict())


@router.post("/auth/logout", status_code=200)
async def logout(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    request: Request = None,
):
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.removeprefix("Bearer ").strip()
    session_uc = ManageSessionUseCase(PostgresSessionRepo(db))
    await session_uc.logout(token)
    return {"logged_out": True}


# ── Calculate ────────────────────────────────────────────────────────────────

@router.post("/calculate", response_model=CalculationResponse)
async def calculate(
    request: CalculationRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    history_repo = PostgresHistoryRepo(db)
    engine = MpMathCalculationEngine()
    uc = EvaluateExpressionUseCase(engine, history_repo, current_user["user_id"])
    return await uc.execute(request)


# ── History ──────────────────────────────────────────────────────────────────

@router.get("/history")
async def get_history(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = PostgresHistoryRepo(db)
    uc = ManageHistoryUseCase(repo)
    items = await uc.get_by_user(current_user["user_id"])
    return [
        {
            "id": c.id,
            "expression": c.expression,
            "result": c.result,
            "precision_digits": c.precision_digits,
            "created_at": c.created_at,
        }
        for c in items
    ]


@router.get("/history/export")
async def export_history(
    format: str = Query(default="json", pattern="^(json|csv)$"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = PostgresHistoryRepo(db)
    uc = ManageHistoryUseCase(repo)
    items = await uc.get_by_user(current_user["user_id"])

    rows = [
        {
            "expression": c.expression,
            "result": c.result,
            "precision_digits": c.precision_digits,
            "created_at": str(c.created_at),
        }
        for c in items
    ]

    if format == "json":
        content = json.dumps(rows, ensure_ascii=False, indent=2)
        return StreamingResponse(
            io.StringIO(content),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=historial_scicalc.json"},
        )

    # CSV
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=["expression", "result", "precision_digits", "created_at"])
    writer.writeheader()
    writer.writerows(rows)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=historial_scicalc.csv"},
    )


@router.delete("/history/{calc_id}", status_code=200)
async def delete_history(
    calc_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = PostgresHistoryRepo(db)
    uc = ManageHistoryUseCase(repo)
    deleted = await uc.delete(calc_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    await PostgresAuditRepo(db).log_action(current_user["user_id"], "calculation_history", calc_id, "DELETE")
    return {"deleted": True, "id": calc_id}


# ── Preferences (memoria RF-004) ─────────────────────────────────────────────

@router.get("/preferences/memory")
async def get_memory(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    uc = ManagePreferencesUseCase(PostgresPreferencesRepo(db))
    value = await uc.get_memory(current_user["user_id"])
    return {"value": value}


@router.post("/preferences/memory", status_code=200)
async def set_memory(
    payload: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    value = payload.get("value")
    if value is None or not isinstance(value, (int, float)):
        raise HTTPException(status_code=422, detail="'value' debe ser un número")
    uc = ManagePreferencesUseCase(PostgresPreferencesRepo(db))
    await uc.set_memory(current_user["user_id"], float(value))
    return {"value": float(value)}


@router.delete("/preferences/memory", status_code=200)
async def clear_memory(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    uc = ManagePreferencesUseCase(PostgresPreferencesRepo(db))
    await uc.clear_memory(current_user["user_id"])
    return {"cleared": True}


# ── Favorite Conversions ─────────────────────────────────────────────────────

@router.get("/conversions/favorites")
async def list_favorites(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    uc = ManageFavoriteConversionsUseCase(PostgresFavoriteConversionRepo(db))
    items = await uc.list(current_user["user_id"])
    return [{"id": f.id, "from_unit": f.from_unit, "to_unit": f.to_unit, "category": f.category} for f in items]


@router.post("/conversions/favorites", status_code=201)
async def create_favorite(
    payload: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    uc = ManageFavoriteConversionsUseCase(PostgresFavoriteConversionRepo(db))
    try:
        fav = await uc.create(
            user_id=current_user["user_id"],
            from_unit=payload.get("from_unit", ""),
            to_unit=payload.get("to_unit", ""),
            category=payload.get("category", ""),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"id": fav.id, "from_unit": fav.from_unit, "to_unit": fav.to_unit, "category": fav.category}


@router.delete("/conversions/favorites/{fav_id}", status_code=200)
async def delete_favorite(
    fav_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    uc = ManageFavoriteConversionsUseCase(PostgresFavoriteConversionRepo(db))
    deleted = await uc.delete(fav_id, current_user["user_id"])
    if not deleted:
        raise HTTPException(status_code=404, detail="Favorito no encontrado")
    return {"deleted": True, "id": fav_id}


# ── Profile ──────────────────────────────────────────────────────────────────

@router.get("/profile")
async def get_profile(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    uc = ManageProfileUseCase(PostgresProfileRepo(db))
    profile = await uc.get(current_user["user_id"])
    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "avatar_url": profile.avatar_url,
        "preferred_precision": profile.preferred_precision,
        "angle_mode": profile.angle_mode,
        "theme": profile.theme,
        "updated_at": profile.updated_at,
    }


@router.put("/profile", status_code=200)
async def update_profile(
    payload: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    uc = ManageProfileUseCase(PostgresProfileRepo(db))
    try:
        profile = await uc.update(
            user_id=current_user["user_id"],
            preferred_precision=payload.get("preferred_precision"),
            angle_mode=payload.get("angle_mode"),
            theme=payload.get("theme"),
            avatar_url=payload.get("avatar_url"),
        )
    except DomainError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "avatar_url": profile.avatar_url,
        "preferred_precision": profile.preferred_precision,
        "angle_mode": profile.angle_mode,
        "theme": profile.theme,
        "updated_at": profile.updated_at,
    }


# ── Users ─────────────────────────────────────────────────────────────────────

@router.get("/users/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user


@router.delete("/users/{user_id}", status_code=200)
async def delete_user(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = PostgresUserRepo(db)
    deleted = await repo.delete_logical(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"deleted": True, "id": user_id}
