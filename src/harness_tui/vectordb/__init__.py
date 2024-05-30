import hashlib
import typing as t
from pathlib import Path

import lancedb
import numpy as np
import pandas as pd


class LogVectorDB:
    """A simple vector database for storing and searching log vectors."""

    TABLE = "vector_idsss"

    def __init__(self, uri, vector_size=128):
        self.uri = uri
        self.vector_size = vector_size
        self._db = None
        self._table = None
        self._new = True

    @property
    def db(self):
        if self._db is None:
            self._db = lancedb.connect(self.uri)
        return self._db

    @property
    def table(self):
        if self._table is None:
            if self.TABLE in list(self.db.table_names()):
                self._table = self.db.open_table(self.TABLE)
                self._new = False
            else:
                self._table = self.db.create_table(self.TABLE)
        return self._table

    def _hash_to_vector(self, s: str) -> t.List[int]:
        """Hash a string to a vector."""
        hash_bytes = hashlib.sha256(s.encode("utf-8")).digest()
        hash_vector = np.frombuffer(hash_bytes, dtype=np.uint8)[: self.vector_size]
        return hash_vector.tolist()

    def _read_logs(self, directory_path: str | Path) -> t.List[t.Dict[str, t.Any]]:
        """Read log files from a directory and hash them to vectors."""
        log_list = []
        for path in Path(directory_path).rglob("*.log"):
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()
            log_list.append(
                {
                    "vector": self._hash_to_vector(str(path) + content),
                    "log_content": content,
                }
            )

        return log_list

    async def search(self, query: str, limit: int = 2) -> pd.DataFrame:
        """Search for similar vectors in the database."""
        if self.table is None:
            raise RuntimeError("Table is not created.")
        return (
            self.table.search(self._hash_to_vector(query))  # type: ignore
            .limit(limit)
            .to_pandas()
        )

    @classmethod
    async def build(cls, log_dir: str | Path):
        """Build a VectorDatabase from a directory of log files."""
        path = Path(log_dir)
        uri = path / "lancedb"
        db = cls(uri)
        if db._new:
            # TODO: add a disk cache
            log_list = db._read_logs(log_dir)
            db.table.add(log_list)
        return db
