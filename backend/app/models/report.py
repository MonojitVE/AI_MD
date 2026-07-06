"""Report ORM model."""

from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

from app.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    report_type = Column(String(50), nullable=False, index=True)  # daily, weekly, monthly, executive, maintenance, equipment, inventory
    content = Column(Text, nullable=False)  # Markdown content
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
