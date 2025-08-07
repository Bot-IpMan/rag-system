"""Simple document retriever module."""
from typing import List


def fetch_relevant(question: str) -> List[str]:
    """Return an empty list of documents for the given question.

    This is a placeholder implementation used for testing the API server
    structure. The real implementation would query a vector store or other
    retrieval component to find documents relevant to *question*.
    """
    return []
