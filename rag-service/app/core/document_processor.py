"""Utilities for loading and chunking documents of various formats.

This module implements :class:`DocumentProcessor` which is responsible for
reading files or URLs, extracting their textual content and splitting it into
chunks ready for embedding and storage in the vector database.  The
implementation focuses on simplicity and uses common Python libraries such as
``PyPDF2`` and ``BeautifulSoup`` so that the component can operate in the
restricted execution environment of the kata.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import requests
from bs4 import BeautifulSoup
from markdown import markdown
import PyPDF2

try:  # DOCX support is optional as ``python-docx`` is fairly heavy
    import docx  # type: ignore

    DOCX_AVAILABLE = True
except Exception:  # pragma: no cover - dependency is optional
    DOCX_AVAILABLE = False


logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process different document formats and split them into chunks.

    Parameters
    ----------
    chunk_size:
        Maximum size of a chunk in characters.
    chunk_overlap:
        Overlap between neighbouring chunks to preserve context.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Map file extensions to processing functions
        self.supported_formats: Dict[str, Any] = {
            ".pdf": self._process_pdf,
            ".txt": self._process_txt,
            ".md": self._process_markdown,
            ".html": self._process_html,
            ".htm": self._process_html,
            ".csv": self._process_csv,
            ".xlsx": self._process_excel,
            ".xls": self._process_excel,
            ".json": self._process_json,
        }

        if DOCX_AVAILABLE:
            self.supported_formats[".docx"] = self._process_docx

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def process_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Read ``file_path`` and return a list of text chunks.

        Each returned item is a dictionary with keys ``text`` and ``metadata``.
        ``metadata`` contains basic information about the source such as file
        name and processing timestamp as well as ``chunk_id`` and
        ``total_chunks``.
        """

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(file_path)

        ext = path.suffix.lower()
        processor = self.supported_formats.get(ext)
        if processor is None:
            raise ValueError(f"Unsupported file format: {ext}")

        text = processor(str(path))
        metadata = {
            "source": str(path),
            "filename": path.name,
            "file_type": ext,
            "file_size": path.stat().st_size,
            "processed_date": datetime.utcnow(),
        }

        return self.chunk_text(text, metadata)

    def process_url(self, url: str) -> Dict[str, Any]:
        """Download and process a web page located at ``url``.

        The function extracts all textual content from the retrieved HTML and
        returns a dictionary with keys ``title``, ``text`` and metadata about
        the request.
        """

        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator="\n")
        title = soup.title.string.strip() if soup.title and soup.title.string else url

        return {
            "url": url,
            "title": title,
            "text": text,
            "processed_date": datetime.utcnow(),
        }

    # ------------------------------------------------------------------
    # Chunking helpers
    # ------------------------------------------------------------------
    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split ``text`` into chunks preserving a small overlap.

        Parameters
        ----------
        text:
            Source text to split.
        metadata:
            Base metadata copied into each chunk's metadata dictionary.
        """

        if not text:
            return []

        chunks: List[Dict[str, Any]] = []
        step = max(self.chunk_size - self.chunk_overlap, 1)

        for start in range(0, len(text), step):
            chunk_text = text[start : start + self.chunk_size]
            chunk_meta = metadata.copy()
            chunk_meta["chunk_id"] = len(chunks)
            chunks.append({"text": chunk_text, "metadata": chunk_meta})

        total = len(chunks)
        for item in chunks:
            item["metadata"]["total_chunks"] = total

        return chunks

    # ------------------------------------------------------------------
    # Processing helpers for individual file types
    # ------------------------------------------------------------------
    def _process_pdf(self, file_path: str) -> str:
        text_parts: List[str] = []
        with open(file_path, "rb") as fh:
            reader = PyPDF2.PdfReader(fh)
            for page in reader.pages:
                text_parts.append(page.extract_text() or "")
        return "\n".join(text_parts)

    def _process_txt(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as fh:
            return fh.read()

    def _process_markdown(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as fh:
            html = markdown(fh.read())
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text()

    def _process_html(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as fh:
            soup = BeautifulSoup(fh.read(), "html.parser")
        return soup.get_text()

    def _process_csv(self, file_path: str) -> str:
        df = pd.read_csv(file_path)
        text = f"Таблиця містить {len(df)} записів з колонками: {list(df.columns)}\n"
        text += df.to_string(index=False)
        return text

    def _process_excel(self, file_path: str) -> str:
        df = pd.read_excel(file_path)
        text = f"Таблиця містить {len(df)} записів з колонками: {list(df.columns)}\n"
        text += df.to_string(index=False)
        return text

    def _process_json(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as fh:
            data = json.load(fh)
        return json.dumps(data, ensure_ascii=False, indent=2)

    def _process_docx(self, file_path: str) -> str:
        if not DOCX_AVAILABLE:  # pragma: no cover - safety check
            raise RuntimeError("python-docx is not available")
        document = docx.Document(file_path)
        return "\n".join(p.text for p in document.paragraphs)


__all__ = ["DocumentProcessor"]

