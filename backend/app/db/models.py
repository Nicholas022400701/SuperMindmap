import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Store embeddings as a JSON string. Use standard Text type for compatibility.
    embedding = Column(Text, nullable=True)

    # Relationships
    children_edges = relationship("Edge", foreign_keys="[Edge.source_id]", back_populates="source", cascade="all, delete-orphan")
    parent_edges = relationship("Edge", foreign_keys="[Edge.target_id]", back_populates="target", cascade="all, delete-orphan")

class Edge(Base):
    __tablename__ = "edges"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("nodes.id"), nullable=False)
    target_id = Column(Integer, ForeignKey("nodes.id"), nullable=False)

    source = relationship("Node", foreign_keys=[source_id], back_populates="children_edges")
    target = relationship("Node", foreign_keys=[target_id], back_populates="parent_edges")
