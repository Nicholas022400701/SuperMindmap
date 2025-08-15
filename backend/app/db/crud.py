from sqlalchemy.orm import Session
from . import models
import json

def get_or_create_object_root(db: Session) -> models.Node:
    object_root = db.query(models.Node).filter(models.Node.title == "ObjectRoot").first()
    if not object_root:
        object_root = models.Node(title="ObjectRoot", content="The single root of the entire mind map graph.")
        db.add(object_root)
        db.commit()
        db.refresh(object_root)
    return object_root

def create_node(db: Session, title: str, content: str = None, embedding: list[float] = None) -> models.Node:
    embedding_str = json.dumps(embedding) if embedding else None
    db_node = models.Node(title=title, content=content, embedding=embedding_str)
    db.add(db_node)
    db.commit()
    db.refresh(db_node)
    return db_node

def create_edge(db: Session, source_id: int, target_id: int) -> models.Edge:
    db_edge = models.Edge(source_id=source_id, target_id=target_id)
    db.add(db_edge)
    db.commit()
    db.refresh(db_edge)
    return db_edge

def get_all_nodes_except(db: Session, node_ids_to_exclude: list[int]) -> list[models.Node]:
    return db.query(models.Node).filter(models.Node.id.notin_(node_ids_to_exclude)).all()

def reparent_children(db: Session, old_parent_id: int, new_parent_id: int):
    db.query(models.Edge).filter(models.Edge.source_id == old_parent_id).update({"source_id": new_parent_id})
    db.commit()

def delete_node_and_parent_edge(db: Session, node_id: int):
    db.query(models.Edge).filter(models.Edge.target_id == node_id).delete()
    db.query(models.Node).filter(models.Node.id == node_id).delete()
    db.commit()

def delete_nodes_by_ids(db: Session, node_ids: list[int]):
    """
    Deletes multiple nodes and all edges connected to them.
    """
    if not node_ids:
        return
    # Delete edges where either source or target is one of the nodes to be deleted
    db.query(models.Edge).filter(
        (models.Edge.source_id.in_(node_ids)) | (models.Edge.target_id.in_(node_ids))
    ).delete(synchronize_session=False)

    # Delete the nodes
    db.query(models.Node).filter(models.Node.id.in_(node_ids)).delete(synchronize_session=False)
    db.commit()

def get_node_by_id(db: Session, node_id: int) -> models.Node:
    return db.query(models.Node).filter(models.Node.id == node_id).first()

def get_children_for_node(db: Session, node_id: int) -> list[models.Node]:
    child_edges = db.query(models.Edge).filter(models.Edge.source_id == node_id).all()
    child_ids = [edge.target_id for edge in child_edges]
    if not child_ids:
        return []
    return db.query(models.Node).filter(models.Node.id.in_(child_ids)).all()

def get_all_nodes(db: Session) -> list[models.Node]:
    return db.query(models.Node).all()

def get_all_edges(db: Session) -> list[models.Edge]:
    return db.query(models.Edge).all()

def get_parent_for_node(db: Session, node_id: int) -> models.Node | None:
    parent_edge = db.query(models.Edge).filter(models.Edge.target_id == node_id).first()
    if not parent_edge:
        return None
    return get_node_by_id(db, parent_edge.source_id)

def update_node_title(db: Session, node_id: int, new_title: str):
    db.query(models.Node).filter(models.Node.id == node_id).update({"title": new_title})
    db.commit()
