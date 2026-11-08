"""Tenant loading. One folder per broker client under tenants/<slug>/.

A new client is a new folder (tenant.json + policy.json), never a new repo.
"""
import json
import re
from functools import lru_cache
from pathlib import Path

TENANTS_DIR = Path(__file__).resolve().parent.parent / "tenants"
_SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,40}$")


class TenantNotFound(Exception):
    pass


@lru_cache(maxsize=64)
def load_tenant(slug: str) -> dict:
    if not _SLUG.match(slug):
        raise TenantNotFound(slug)
    folder = TENANTS_DIR / slug
    cfg_path = folder / "tenant.json"
    if not cfg_path.is_file():
        raise TenantNotFound(slug)
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    policy_path = folder / cfg["policy_file"]
    cfg["policy"] = json.loads(policy_path.read_text(encoding="utf-8"))
    return cfg


def public_config(tenant: dict) -> dict:
    """Only what the browser may see."""
    return {
        "slug": tenant["slug"],
        "display_name": tenant["display_name"],
        "languages": tenant["languages"],
        "default_language": tenant["default_language"],
        "modules": tenant["modules"],
        "brand": tenant["brand"],
    }
