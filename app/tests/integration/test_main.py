from fastapi.testclient import TestClient
from app.main import app
from app.core import config

client = TestClient(app)


def get_auth_headers():
    # Use a valid hardcoded tenant API key from config.py
    return {"x-api-key": list(config.settings.HARDCODED_TENANTS.keys())[0]}

def test_ping():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_crud_tool():
    # Create a tool
    data = {"name": "Update Tool", "description": "To be updated."}
    resp = client.post("/tools", json=data, headers=get_auth_headers())
    tool = resp.json()
    tool_id = tool["id"]
    assert tool_id is not None
    # Update it
    update_data = {"name": "Updated Tool", "description": "Updated description."}
    response = client.put(f"/tools/{tool_id}", json=update_data, headers=get_auth_headers())
    assert response.status_code == 200
    updated = response.json()
    assert updated["name"] == update_data["name"]
    assert updated["description"] == update_data["description"]
    # Validate tool changed
    get_resp = client.get("/tools", headers=get_auth_headers())
    assert any(t["id"] == tool_id and t["name"] == update_data["name"] for t in get_resp.json())
    # Clean up tool
    response = client.delete(f"/tools/{tool_id}", headers=get_auth_headers())
    assert response.status_code == 200
    assert response.json()["ok"] is True

def test_crud_agent_with_tool():
    # Create a tool and agent
    tool_data = {"name": "Update Agent Tool", "description": "Tool for agent update."}
    tool_resp = client.post("/tools", json=tool_data, headers=get_auth_headers())
    tool_id = tool_resp.json()["id"]
    agent_data = {
        "name": "AgentToUpdate",
        "role": "updater",
        "description": "Agent to be updated.",
        "tool_ids": [tool_id]
    }
    agent_resp = client.post("/agents", json=agent_data, headers=get_auth_headers())
    agent = agent_resp.json()
    agent_id = agent["id"]
    # Update agent
    update_data = {
        "name": "UpdatedAgent",
        "role": "updated-role",
        "description": "Updated agent description.",
        "tool_ids": [tool_id]
    }
    response = client.put(f"/agents/{agent_id}", json=update_data, headers=get_auth_headers())
    assert response.status_code == 200
    updated = response.json()
    assert updated["name"] == update_data["name"]
    assert updated["role"] == update_data["role"]
    assert updated["description"] == update_data["description"]
    # Validate agent changed
    get_resp = client.get("/agents", headers=get_auth_headers())
    assert any(a["id"] == agent_id and a["name"] == update_data["name"] for a in get_resp.json())
    # Clean up agent
    response = client.delete(f"/agents/{agent_id}", headers=get_auth_headers())
    assert response.status_code == 200
    assert response.json()["ok"] is True
    # Clean up tool
    response = client.delete(f"/tools/{tool_id}", headers=get_auth_headers())
    assert response.status_code == 200
    assert response.json()["ok"] is True

def test_run_agent_and_list_executions():
    # Create tool and agent
    tool_data = {"name": "Exec Tool", "description": "Tool for execution."}
    tool_resp = client.post("/tools", json=tool_data, headers=get_auth_headers())
    tool_id = tool_resp.json()["id"]
    agent_data = {
        "name": "ExecAgent",
        "role": "runner",
        "description": "Agent for execution.",
        "tool_ids": [tool_id]
    }
    agent_resp = client.post("/agents", json=agent_data, headers=get_auth_headers())
    agent_id = agent_resp.json()["id"]
    assert agent_id is not None
    # Run agent (dummy task/model)
    run_data = {"task": "Say hello", "model": "test-model"}
    run_resp = client.post(f"/agents/{agent_id}/run", json=run_data, headers=get_auth_headers())
    # Accept 200
    assert run_resp.status_code == 200
    result = run_resp.json()
    assert "final_response" in result
    assert "tool_calls" in result
    assert "prompt" in result
    # List executions
    exec_resp = client.get(f"/agents/{agent_id}/executions", headers=get_auth_headers())
    assert exec_resp.status_code == 200
    executions = exec_resp.json()
    assert isinstance(executions, list)
    # Clean up tool
    response = client.delete(f"/tools/{tool_id}", headers=get_auth_headers())
    assert response.status_code == 200
    assert response.json()["ok"] is True
    # Clean up agent
    response = client.delete(f"/agents/{agent_id}", headers=get_auth_headers())
    assert response.status_code == 200
    assert response.json()["ok"] is True