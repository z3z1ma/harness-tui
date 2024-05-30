import hashlib
import json
import os
import typing as t

import lancedb
import numpy as np


class VectorDatabase:

    def __init__(self, uri, vector_size=128):
        self.uri = uri
        self.vector_size = vector_size
        self.async_db = None
        self.async_tbl = None

    async def connect(self):
        self.async_db = await lancedb.connect_async(self.uri)

    async def table_exists(self, table_name):
        if self.async_db is None:
            raise RuntimeError("Database is not connected.")
        tables = await self.async_db.table_names()
        return table_name in tables

    async def create_table(self, table_name: str, data: t.Any):
        if self.async_db is None:
            raise RuntimeError("Database is not connected.")
        if not await self.table_exists(table_name):
            self.async_tbl = await self.async_db.create_table(table_name,
                                                              data=data)
        else:
            self.async_tbl = await self.async_db.open_table(table_name)

    def hash_to_vector(self, s: str):
        hash_bytes = hashlib.sha256(s.encode("utf-8")).digest()
        hash_vector = np.frombuffer(hash_bytes,
                                    dtype=np.uint8)[:self.vector_size]
        return hash_vector.tolist()

    def get_log_dict_from_directory(self, directory_path: str):
        log_list = []
        for root, _, files in os.walk(directory_path):
            print("root",root)
            for file in files:
                if file != ".DS_Store":
                    full_path = os.path.join(root, file)
                    with open(full_path, "r", encoding="utf-8") as file:
                        content = file.read()

                    try:
                        log_entries = [
                            json.loads(line)
                            for line in content.strip().split("\n")
                        ]
                        obj = {
                            "vector": self.hash_to_vector(full_path+str(log_entries)),
                            "log_content": str(log_entries),
                        }
                        log_list.append(obj)
                        print(obj)
                    except json.JSONDecodeError:
                        print(
                            f"The file content in {full_path} is not valid JSON."
                        )
                        print(content)

        return log_list

    async def vector_search(self, query: str, limit: int = 2):
        if self.async_tbl is None:
            raise RuntimeError("Table is not created.")
        return (await self.async_tbl.vector_search(self.hash_to_vector(query)
                                                   )  # type: ignore
                .limit(limit).to_pandas())


# Uncomment to test code
async def main():
    uri = "data/sample-lancedb"
    db = VectorDatabase(uri)
    await db.connect()

    directory_path = "./logs/"
    log_list = db.get_log_dict_from_directory(directory_path)
    print("log_list",log_list)
    await db.create_table("vector_idsss", log_list)

    search_result = await db.vector_search("Aqua")
    print(search_result)

# Running the async main function
import asyncio
asyncio.run(main())
