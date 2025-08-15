from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db
from app.services.mindmap_service import mindmap_service
from app.db import crud

router = APIRouter()

class AddKeywordRequest(BaseModel):
    keyword: str

@router.post("/add", response_model=dict)
async def add_mind_map(
    request: AddKeywordRequest,
    db: Session = Depends(get_db)
):
    """
    Adds a new mind map based on a keyword. This is an async endpoint.
    """
    if request.keyword.lower() == "objectroot":
        raise HTTPException(status_code=400, detail="Operations on ObjectRoot are not allowed.")

    generated_map = await mindmap_service.add_mind_map(request.keyword, db)

    if generated_map is None:
        raise HTTPException(status_code=500, detail="Failed to generate mind map from AI service.")

    return generated_map

@router.get("/export/{node_id}", response_model=dict)
def export_mind_map(
    node_id: int,
    db: Session = Depends(get_db)
):
    """
    Exports a mind map or subgraph to JSON, starting from the given node_id.
    """
    exported_map = mindmap_service.export_mindmap(node_id, db)
    if exported_map is None:
        raise HTTPException(status_code=404, detail="Node not found.")

    return exported_map

@router.get("/graph", response_model=dict)
def get_full_graph(db: Session = Depends(get_db)):
    """
    Fetches the entire graph of nodes and links for visualization.
    """
    return mindmap_service.get_graph(db)

@router.delete("/nodes/{node_id}", status_code=204)
def delete_node_tree_endpoint(
    node_id: int,
    db: Session = Depends(get_db)
):
    """
    Deletes a node and its entire subtree.
    """
    # Prevent deleting the root node
    object_root = crud.get_or_create_object_root(db)
    if node_id == object_root.id:
        raise HTTPException(status_code=400, detail="Cannot delete the root node.")

    mindmap_service.delete_node_tree(node_id, db)
    return Response(status_code=204)
