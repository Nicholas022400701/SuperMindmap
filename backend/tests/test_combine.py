from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.db import crud
import pytest

# --- Mock Data ---
MOCK_AI_RESPONSE_A = {
    "title": "Learning Python",
    "children": [{"title": "Core Concepts", "children": [{"title": "Variables", "children": []}]}],
}
MOCK_AI_RESPONSE_B = {
    "title": "Python Basics",
    "children": [{"title": "Fundamentals", "children": [{"title": "Variables and Types", "children": []}]}],
}

# Pre-defined embeddings for the test. Using orthogonal vectors for clarity.
EMBEDDINGS = {
    # These two are identical, should merge (similarity = 1.0)
    "Variables":           [1.0, 0.0, 0.0, 0.0],
    "Variables and Types": [1.0, 0.0, 0.0, 0.0],

    # These are all distinct and orthogonal (similarity = 0.0)
    "Core Concepts":       [0.0, 1.0, 0.0, 0.0],
    "Fundamentals":        [0.0, 0.0, 1.0, 0.0],
    "Learning Python":     [0.0, 0.0, 0.0, 1.0],
    "Python Basics":       [0.0, 0.0, 0.0, 0.0], # Make this one different from the root
}


# --- Test Function ---
@pytest.mark.asyncio
async def test_combine_on_add(client: TestClient, db_session: Session, monkeypatch):
    # 1. Mock the services
    from app.services.ai_service import ai_service
    from app.services.similarity_service import similarity_service

    ai_call_count = 0
    def mock_generate_mindmap(keyword: str):
        nonlocal ai_call_count
        ai_call_count += 1
        return MOCK_AI_RESPONSE_A if ai_call_count == 1 else MOCK_AI_RESPONSE_B

    async def mock_get_embedding(text: str):
        # Return a pre-defined embedding or a default zero vector for any other text
        return EMBEDDINGS.get(text, [0.0, 0.0, 0.0, 0.0])

    monkeypatch.setattr(ai_service, "generate_mindmap", mock_generate_mindmap)
    monkeypatch.setattr(similarity_service, "get_embedding", mock_get_embedding)

    # 2. Add the first mind map
    response_a = client.post("/api/add", json={"keyword": "Learning Python"})
    assert response_a.status_code == 200

    # Verify initial state: 1(ObjectRoot) + 3(MapA) = 4 nodes
    assert db_session.query(crud.models.Node).count() == 4

    # 3. Add the second mind map
    response_b = client.post("/api/add", json={"keyword": "Python Basics"})
    assert response_b.status_code == 200

    # 4. Verify the new renaming logic
    # Instead of merging, the two similar nodes should be renamed for disambiguation.

    # Total nodes should be 4 (Map A) + 3 (Map B) = 7. No nodes are deleted.
    # Note: The count includes the global "ObjectRoot" node.
    # So, 1 (ObjectRoot) + 3 (MapA) + 3 (MapB) = 7
    assert db_session.query(crud.models.Node).count() == 7, "No nodes should be deleted"

    # The original titles should no longer exist as they have been renamed.
    original_a_query = db_session.query(crud.models.Node).filter_by(title="Variables")
    assert original_a_query.count() == 0, "Original node 'Variables' should have been renamed"

    original_b_query = db_session.query(crud.models.Node).filter_by(title="Variables and Types")
    assert original_b_query.count() == 0, "Original node 'Variables and Types' should have been renamed"

    # The new, disambiguated titles should exist.
    renamed_a_query = db_session.query(crud.models.Node).filter_by(title="Variables (from Core Concepts)")
    assert renamed_a_query.count() == 1, "Node 'Variables' should be renamed with its parent context"

    renamed_b_query = db_session.query(crud.models.Node).filter_by(title="Variables and Types (from Fundamentals)")
    assert renamed_b_query.count() == 1, "Node 'Variables and Types' should be renamed with its parent context"

    # Verify that the parent relationships are still correct for the renamed nodes.
    renamed_a_node = renamed_a_query.one()
    parent_a_edge = db_session.query(crud.models.Edge).filter_by(target_id=renamed_a_node.id).one()
    parent_a_node = crud.get_node_by_id(db_session, parent_a_edge.source_id)
    assert parent_a_node.title == "Core Concepts"

    renamed_b_node = renamed_b_query.one()
    parent_b_edge = db_session.query(crud.models.Edge).filter_by(target_id=renamed_b_node.id).one()
    parent_b_node = crud.get_node_by_id(db_session, parent_b_edge.source_id)
    assert parent_b_node.title == "Fundamentals"
