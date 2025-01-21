import logging
from typing import List, Optional

import openai
import pandas as pd
from sqlalchemy import inspect, select

from app.core.settings import settings
from app.db.base import Base
from app.db.models.record import Record
from app.db.session import SessionLocal, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStore:  # noqa: D101
    def __init__(self) -> None:
        self.engine = engine
        self.Session = SessionLocal
        self.openai_api_key = settings.open_api_key
        self.embedding_model = settings.embedding_model
        openai.api_key = self.openai_api_key


    async def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for the given text using OpenAI API."""
        text = text.replace("\n", " ")
        response = openai.Embedding.create(input=[text], model=self.embedding_model)
        return response["data"][0]["embedding"]

    async def create_tables(self) -> None:
        """Create necessary tables and indexes in the database."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def table_exists(self) -> bool:
        """
        Check if the table exists in the database.

        Returns:
            bool: True if the table exists, False otherwise.
        """
        async with self.engine.connect() as conn:
            # Sử dụng `run_sync` để chạy các hàm đồng bộ trong một môi trường bất đồng bộ
            return await conn.run_sync(
                lambda sync_conn: inspect(sync_conn).has_table(Record.__tablename__)
            )

    async def drop_tables(self) -> None:
        """Drop the necessary tables from the database."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def upsert(self, records: pd.DataFrame) -> None:
        """Insert or update records in the database from a pandas DataFrame."""
        async with self.Session() as session, session.begin():
            for _, row in records.iterrows():
                try:
                    logger.info(
                        f"Processing row {row['id']} with metadata {row['metadata']}",
                    )
                    record = await session.merge(
                        Record(
                            id=row["id"],
                            record_metadata=row["metadata"],
                            contents=row["contents"],
                            embedding=row["embedding"],
                        ),
                    )
                    session.add(record)
                except Exception as e:
                    logger.error(f"Error processing row {row['id']}: {e}")
            await session.commit()

    async def search(
        self, query_text: str, limit: int = 10, metadata_filter: Optional[dict] = None,
    ) -> List[dict]:
        """Query the vector database for similar embeddings based on input text."""
        query_embedding = await self.get_embedding(query_text)
        async with self.Session() as session:
            query = (
                select(
                    Record,
                    Record.embedding.l2_distance(query_embedding).label("distance"),
                )
                .order_by("distance")
                .limit(limit)
            )
            if metadata_filter:
                for key, value in metadata_filter.items():
                    query = query.filter(
                        Record.record_metadata[key].astext == str(value),
                    )

            results = await session.execute(query)
        fetched_results = results.fetchall()
        return [
            {
                "id": record.id,
                "contents": record.contents,
                "metadata": record.record_metadata,
                "score": 1 - distance,
            }
            for record, distance in fetched_results
            if (1 - distance) > 0
        ]

    async def delete(
        self,
        ids: Optional[List[str]] = None,
        metadata_filter: Optional[dict] = None,
        delete_all: bool = False,
    ) -> None:
        """Delete records from the database based on specified criteria."""
        if sum(bool(x) for x in (ids, metadata_filter, delete_all)) != 1:
            raise ValueError(
                "Provide exactly one of: ids, metadata_filter, or delete_all",
            )

        async with self.Session() as session:  # noqa: SIM117
            async with session.begin():
                if delete_all:
                    await session.execute(Record.__table__.delete())
                elif ids:
                    await session.execute(
                        Record.__table__.delete().where(Record.id.in_(ids)),
                    )
                elif metadata_filter:
                    query = Record.__table__.delete()
                    for key, value in metadata_filter.items():
                        query = query.where(
                            Record.record_metadata[key].astext == str(value),
                        )
                    await session.execute(query)
                await session.commit()
