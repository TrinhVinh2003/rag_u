import uuid  # noqa: N999

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, Column, Text
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Record(Base):
    """
    Represents a record in the database.

    Attributes:
        id (UUID): The primary key of the record, automatically generated using UUID.
        record_metadata (JSON): Metadata associated with the record, stored as JSON.
        contents (Text): The main content of the record, cannot be null.
        embedding (Vector): The vector representation of the record, cannot be null.
    """

    __tablename__ = "records"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        comment="Primary key of the record, automatically generated using UUID.",
    )
    record_metadata = Column(
        JSON,
        nullable=True,
        comment="Metadata associated with the record, stored as JSON.",
    )
    contents = Column(
        Text,
        nullable=False,
        comment="The main content of the record, cannot be null.",
    )
    embedding = Column(
        Vector(1536),
        nullable=False,
        comment="The vector representation of the record, cannot be null.",
    )

    def __repr__(self) -> str:
        """
        Returns a string representation of the Record object.

        Returns:
            str: A string representation of the Record object.
        """
        return (
            f"Record(id={self.id}, "
            f"contents={self.contents[:50]}..., "
            f"metadata={self.record_metadata})"
        )
