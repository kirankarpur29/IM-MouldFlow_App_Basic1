from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    customer_name = Column(String(200))
    designer_name = Column(String(200))

    status = Column(String(50), default="draft")  # draft, analyzed, reported
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    parts = relationship("Part", back_populates="project", cascade="all, delete-orphan")
