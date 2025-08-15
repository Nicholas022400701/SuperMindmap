from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.db import crud
import pytest

# Mock Data
MOCK_AI_RESPONSE = {
    "title": "Test Keyword",
    "children": [
        {"title": "Child 1", "children": []},
        {"title": "Child 2", "children": [{"title": "Grandchild 2.1", "children": []}]},
    ],
}
MOCK_EMBEDDING = [0.1, 0.2, 0.3, 0.4]

@pytest.mark.asyncio
async def test_add_mind_map(client: TestClient, db_session: Session, monkeypatch):
    # Mock the AI service
    def mock_generate_mindmap(keyword: str):
        response_copy = MOCK_AI_RESPONSE.copy()
        response_copy["title"] = keyword
        return response_copy

    # Mock the Similarity service
    async def mock_get_embedding(text: str):
        return MOCK_EMBEDDING

    from app.services.ai_service import ai_service
    from app.services.similarity_service import similarity_service
    monkeypatch.setattr(ai_service, "generate_mindmap", mock_generate_mindmap)
    monkeypatch.setattr(similarity_service, "get_embedding", mock_get_embedding)

    # Action
    response = client.post("/api/add", json={"keyword": "Test Keyword"})

    # Assertions
    assert response.status_code == 200
    assert response.json()["title"] == "Test Keyword"

    db_root_node = crud.get_node_by_id(db_session, 2)
    assert db_root_node is not None
    assert db_root_node.title == "Test Keyword"
    assert db_root_node.embedding is not None

    parent_edge = db_session.query(crud.models.Edge).filter_by(target_id=db_root_node.id).first()
    assert parent_edge is not None
    assert parent_edge.source_id == 1

    children = crud.get_children_for_node(db_session, db_root_node.id)
    assert len(children) == 2

@pytest.mark.asyncio
async def test_add_mind_map_rejects_objectroot(client: TestClient):
    response = client.post("/api/add", json={"keyword": "ObjectRoot"})
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_export_mind_map(client: TestClient, db_session: Session, monkeypatch):
    # Mock services
    from app.services.ai_service import ai_service
    from app.services.similarity_service import similarity_service

    async def mock_get_embedding(text: str):
        return MOCK_EMBEDDING

    monkeypatch.setattr(ai_service, "generate_mindmap", lambda k: MOCK_AI_RESPONSE)
    monkeypatch.setattr(similarity_service, "get_embedding", mock_get_embedding)

    # Add a map first
    client.post("/api/add", json={"keyword": "Test Keyword"})

    # Export
    response = client.get("/api/export/2")
    assert response.status_code == 200
    exported_data = response.json()
    assert exported_data["title"] == "Test Keyword"
    assert len(exported_data["children"]) == 2
