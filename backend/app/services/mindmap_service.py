from sqlalchemy.orm import Session
from app.services.ai_service import ai_service
from app.services.similarity_service import similarity_service
from app.db import crud
from app.db.models import Node
import json
import asyncio

class MindMapService:
    async def add_mind_map(self, keyword: str, db: Session):
        mind_map_data = ai_service.generate_mindmap(keyword)
        if not mind_map_data:
            return None

        object_root = crud.get_or_create_object_root(db)

        newly_created_nodes = []
        await self._add_node_recursively(db, mind_map_data, object_root.id, newly_created_nodes)

        await self._merge_similar_nodes(db, newly_created_nodes)

        return mind_map_data

    async def _add_node_recursively(self, db: Session, node_data: dict, parent_node_id: int, new_nodes_list: list):
        title = node_data.get("title")
        children = node_data.get("children", [])
        if not title:
            return

        content = title
        embedding = await similarity_service.get_embedding(content)

        new_node = crud.create_node(db, title=title, content=content, embedding=embedding)
        crud.create_edge(db, source_id=parent_node_id, target_id=new_node.id)
        new_nodes_list.append(new_node)

        # Process children concurrently
        child_tasks = [self._add_node_recursively(db, child_data, new_node.id, new_nodes_list) for child_data in children]
        await asyncio.gather(*child_tasks)

    async def _merge_similar_nodes(self, db: Session, new_nodes: list[Node]):
        if not new_nodes:
            return

        new_node_ids = [node.id for node in new_nodes]
        object_root = crud.get_or_create_object_root(db)
        ids_to_exclude = new_node_ids + [object_root.id]
        existing_nodes = crud.get_all_nodes_except(db, ids_to_exclude)

        for new_node in new_nodes:
            new_node_embedding = json.loads(new_node.embedding) if new_node.embedding else []
            if not new_node_embedding:
                continue

            for existing_node in existing_nodes:
                existing_node_embedding = json.loads(existing_node.embedding) if existing_node.embedding else []
                if not existing_node_embedding:
                    continue

                similarity = similarity_service.cosine_similarity(new_node_embedding, existing_node_embedding)

                if similarity > 0.95:
                    # --- Start of new renaming logic ---
                    # A similarity conflict is found. We rename both nodes to make them distinct.

                    # 1. Rename the existing node
                    existing_parent = crud.get_parent_for_node(db, existing_node.id)
                    if existing_parent and "(from " not in existing_node.title:
                        new_title_for_existing = f"{existing_node.title} (from {existing_parent.title})"
                        crud.update_node_title(db, existing_node.id, new_title_for_existing)
                        print(f"Disambiguating existing node {existing_node.id} to '{new_title_for_existing}'")
                        # We need to update the python object as well for subsequent checks
                        existing_node.title = new_title_for_existing


                    # 2. Rename the new node
                    new_parent = crud.get_parent_for_node(db, new_node.id)
                    if new_parent and "(from " not in new_node.title:
                        new_title_for_new = f"{new_node.title} (from {new_parent.title})"
                        crud.update_node_title(db, new_node.id, new_title_for_new)
                        print(f"Disambiguating new node {new_node.id} to '{new_title_for_new}'")
                        # We need to update the python object as well for subsequent checks
                        new_node.title = new_title_for_new

                    # 3. Break the inner loop to process the next new_node
                    # This specific conflict has been resolved.
                    break
                    # --- End of new renaming logic ---

    def export_mindmap(self, node_id: int, db: Session) -> dict:
        root_node = crud.get_node_by_id(db, node_id)
        if not root_node:
            return None
        return self._build_export_tree(db, root_node)

    def _build_export_tree(self, db: Session, node: Node) -> dict:
        children = crud.get_children_for_node(db, node.id)
        return {
            "id": node.id,
            "title": node.title,
            "content": node.content,
            "created_at": node.created_at.isoformat(),
            "children": [self._build_export_tree(db, child) for child in children]
        }

    def delete_node_tree(self, node_id: int, db: Session):
        """
        Deletes a node and its entire subtree.
        """
        all_ids_to_delete = self._get_all_descendant_ids(db, node_id)
        all_ids_to_delete.add(node_id)
        crud.delete_nodes_by_ids(db, list(all_ids_to_delete))

    def _get_all_descendant_ids(self, db: Session, node_id: int) -> set[int]:
        """
        Recursively fetches all descendant IDs for a given node.
        """
        children = crud.get_children_for_node(db, node_id)
        descendant_ids = set()
        for child in children:
            descendant_ids.add(child.id)
            descendant_ids.update(self._get_all_descendant_ids(db, child.id))
        return descendant_ids

    def get_graph(self, db: Session) -> dict:
        """
        Fetches all nodes and edges for graph visualization.
        """
        nodes = crud.get_all_nodes(db)
        edges = crud.get_all_edges(db)

        # Format for react-force-graph
        graph_nodes = [{"id": node.id, "name": node.title, "val": 1} for node in nodes]
        graph_links = [{"source": edge.source_id, "target": edge.target_id} for edge in edges]

        return {"nodes": graph_nodes, "links": graph_links}

mindmap_service = MindMapService()
