import os

import pytest
from fastapi.testclient import TestClient

os.environ.pop("ANTHROPIC_API_KEY", None)  # tests run offline

from app.main import app  # noqa: E402

client = TestClient(app)


def chat(msg, slug="demo"):
    return client.post(f"/api/{slug}/copilot/chat", json={"message": msg})


def test_health():
    assert client.get("/health").json() == {"ok": True}


def test_config_hides_policy():
    data = client.get("/api/demo/config").json()
    assert data["slug"] == "demo" and "policy" not in data


def test_known_fact_with_page_source():
    r = chat("Do I need prior approval for hospital admission?").json()
    assert r["kind"] == "facts"
    assert any(s["id"] == "hospital-prior-approval" and s["page"] == 7 for s in r["sources"])


def test_unknown_question_hands_off_not_guesses():
    r = chat("Is skydiving covered?").json()
    assert r["kind"] == "handoff"
    assert "broker@example.com" in r["reply"]


def test_emergency_short_circuits():
    r = chat("My father has a heart attack").json()
    assert r["kind"] == "emergency" and "112" in r["reply"]


@pytest.mark.parametrize("slug", ["nope", "../etc", "Demo"])
def test_bad_tenant_404(slug):
    assert chat("hello", slug).status_code == 404
