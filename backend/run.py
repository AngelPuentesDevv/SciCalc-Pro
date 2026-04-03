"""
Script de arranque para Windows.
Fija WindowsSelectorEventLoopPolicy ANTES de que uvicorn inicie el event loop.
asyncpg requiere SelectorEventLoop — ProactorEventLoop (default en Windows) no funciona.

Notas:
- reload=False es obligatorio en Windows cuando se usa asyncpg: el reloader de uvicorn
  lanza un proceso hijo que NO hereda la política del event loop, revirtiendo a ProactorEventLoop.
- loop="none" le dice a uvicorn que NO cree su propio event loop, dejando que Python
  use el que ya creamos con WindowsSelectorEventLoopPolicy.
"""

import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="127.0.0.1",
        port=8001,
        reload=False,
        loop="none",
    )
