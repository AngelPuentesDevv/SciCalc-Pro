from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

web_router = APIRouter(prefix="/web", tags=["web"])


@web_router.get("/login", response_class=HTMLResponse)
async def web_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@web_router.get("/register", response_class=HTMLResponse)
async def web_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@web_router.get("/calculator", response_class=HTMLResponse)
async def web_calculator(request: Request):
    return templates.TemplateResponse("calculator.html", {"request": request})
