from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)

    report_type = Column(String(20))  # designer, customer
    format = Column(String(10))  # pdf, html, excel
    file_path = Column(String(500))
    generated_at = Column(DateTime, server_default=func.now())

    # Relationships
    analysis = relationship("Analysis", back_populates="reports")
