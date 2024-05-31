"""A simple agent for answering questions based on log files."""

from __future__ import annotations

import random
import typing as t
from pathlib import Path

from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_community.vectorstores import LanceDB
from langchain_core.prompts import ChatPromptTemplate

EMBEDDINGS = OllamaEmbeddings()
PROMPT = ChatPromptTemplate.from_template(
    """Answer the following question based on the provided log file information:

<context>
{context}
</context>

Question: {input}"""
)
CHAIN = create_stuff_documents_chain(Ollama(model="llama2"), PROMPT)

FILTERED_STEPS = [
    "save-cache-harness",
    "restore-cache-harness",
    "liteEngineTask",
]

SAMPLE_SIZE = 100
"""The number of log files to sample when loading the logs."""


def predicate(path: Path) -> bool:
    return not any(step.lower() in path.stem.lower() for step in FILTERED_STEPS)


class LogAgent:
    """A simple agent for answering questions based on log files."""

    def __init__(self, directory: t.Union[str, Path]):
        self.directory = Path(directory)
        self.responder = None

    def load(self):
        """Load the logs from the provided directory and return a responder."""
        documents = []
        paths = list(filter(predicate, Path(self.directory).rglob("*.log")))
        random.shuffle(paths)
        sample_size = min(SAMPLE_SIZE, len(paths))
        if paths:
            for path in paths[:sample_size]:
                loader = TextLoader(path)
                docs = loader.load()
                documents.extend(docs)
        vector = LanceDB.from_documents(documents, EMBEDDINGS)
        retriever = vector.as_retriever()
        self.responder = create_retrieval_chain(retriever, CHAIN)

    def answer(self, question: str) -> str:
        if not self.responder:
            raise ValueError("You must load the logs before asking a question.")
        response = self.responder.invoke({"input": question})
        return response["answer"]
