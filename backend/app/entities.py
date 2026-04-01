from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class WorkflowEntity(Base):
    __tablename__ = "workflows"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    owner_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    nodes: Mapped[list[dict]] = mapped_column(JSON, nullable=False)
    edges: Mapped[list[dict]] = mapped_column(JSON, nullable=False)
