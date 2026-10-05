import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

PORT = 8011
_tmp = tempfile.mkdtemp()
os.environ["BA_DB"] = str(Path(_tmp) / "test.db")
os.environ["BA_MCP_PORT"] = str(PORT)
os.environ["BA_MCP_URL"] = f"http://127.0.0.1:{PORT}/mcp"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

BACKEND = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session", autouse=True)
def mcp_proc():
    p = subprocess.Popen([sys.executable, "-m", "mcp_server.server"], cwd=BACKEND, env=os.environ.copy(),
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(100):
        try:
            socket.create_connection(("127.0.0.1", PORT), timeout=0.2).close()
            break
        except OSError:
            time.sleep(0.1)
    yield
    p.terminate()


@pytest.fixture()
def client():
    from main import app
    c = TestClient(app)
    c.post("/api/demo/reset")
    return c


@pytest.fixture()
def approved(client):
    """Session 1: human approves B-boundary; returns (client, boundary_id)."""
    s1 = client.post("/api/session").json()["id"]
    b = client.post("/api/boundaries/propose", json={}).json()
    r = client.post(f"/api/boundaries/{b['id']}/approve", json={"actor": "HUMAN", "session_id": s1})
    assert r.status_code == 200
    return client, b["id"]


def say(client, text):
    sid = client.post("/api/session").json()["id"]
    return client.post("/api/agent/message", json={"session_id": sid, "text": text}).json()
