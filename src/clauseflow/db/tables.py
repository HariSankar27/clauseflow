import uuid

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class DocumentRow(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    source_file: Mapped[str] = mapped_column(String, nullable=False)
    content_hash: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    full_text: Mapped[str] = mapped_column(String, nullable=False)

    fields: Mapped[list["ExtractedFieldRow"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )


class ExtractedFieldRow(Base):
    __tablename__ = "extracted_fields"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), nullable=False)
    field_name: Mapped[str] = mapped_column(String, nullable=False)
    value: Mapped[str | None] = mapped_column(String)
    evidence_quote: Mapped[str | None] = mapped_column(String)
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    document: Mapped[DocumentRow] = relationship(back_populates="fields")
