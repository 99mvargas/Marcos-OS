from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import captures, finance, health, statements

app = FastAPI(title="Marcos API", version="0.1")

# No auth/cookies in use yet, and the dashboard must be reachable from
# devices other than localhost (e.g. a phone on the same network), so
# origins can't be pinned to a single dev-server host.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(finance.router)
app.include_router(statements.router)
app.include_router(captures.router)
