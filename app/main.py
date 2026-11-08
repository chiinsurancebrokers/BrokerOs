"""Broker OS API. Each module (copilot first) is mounted per tenant."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from . import copilot
from .tenants import TenantNotFound, load_tenant, public_config

app = FastAPI(title="Broker OS", version="0.1.0")


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    lang: str | None = None


def _tenant(slug: str) -> dict:
    try:
        return load_tenant(slug)
    except TenantNotFound:
        raise HTTPException(status_code=404, detail="Unknown tenant")


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/api/{slug}/config")
def config(slug: str):
    return public_config(_tenant(slug))


@app.post("/api/{slug}/copilot/chat")
def copilot_chat(slug: str, body: ChatIn):
    tenant = _tenant(slug)
    if "copilot" not in tenant["modules"]:
        raise HTTPException(status_code=404, detail="Module not enabled")
    return copilot.answer(tenant, body.message, body.lang)
