"""
multi_agent_system.rag.graph_store
=================================
Lưu trữ và quản lý Đồ thị tri thức (NetworkX DiGraph) và Cơ sở dữ liệu Vector (ChromaDB).
"""

import os
import networkx as nx
import chromadb
from typing import List, Dict, Any, Optional, Union
import httpx

from .. import config
from .ast_extractor import CodeChunk

class GraphKnowledgeStore:
    def __init__(self, chroma_dir: Optional[str] = None, graph_file: Optional[str] = None):
        self.chroma_dir = chroma_dir or config.CHROMA_DB_DIR
        self.graph_file = graph_file or config.GRAPH_FILE_PATH
        self.graph: nx.DiGraph = nx.DiGraph()
        self.chroma_client: Optional[chromadb.PersistentClient] = None
        self.collection = None

    def _init_chroma(self):
        if self.chroma_client is None:
            os.makedirs(self.chroma_dir, exist_ok=True)
            self.chroma_client = chromadb.PersistentClient(path=self.chroma_dir)
            try:
                self.collection = self.chroma_client.get_or_create_collection(
                    name=config.COLLECTION_NAME,
                    metadata={"hnsw:space": "cosine"}
                )
            except Exception as e:
                print(f"⚠️ [GraphKnowledgeStore] Lỗi khởi tạo ChromaDB collection: {e}")

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Lấy vector embedding từ Ollama, fallback zero vector nếu lỗi."""
        if not texts:
            return []
        
        url = f"{config.OLLAMA_BASE_URL.rstrip('/')}/api/embed"
        payload = {
            "model": config.EMBEDDING_MODEL,
            "input": texts
        }
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    return data.get("embeddings", [])
        except Exception:
            pass

        # Fallback dummy embeddings nếu Ollama embedding chưa bật
        return [[0.0] * 384 for _ in texts]

    async def build_from_chunks(self, graph: nx.DiGraph, chunks: List[Union[CodeChunk, Dict[str, Any]]]):
        self.graph = graph
        # Lưu đồ thị ra file
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self.graph_file)), exist_ok=True)
            nx.write_gml(self.graph, self.graph_file)
        except Exception as e:
            print(f"⚠️ [GraphKnowledgeStore] Không thể ghi file GML: {e}")

        if not chunks:
            return

        self._init_chroma()
        if self.collection is None:
            return

        # Hỗ trợ cả CodeChunk instance và dictionary
        contents = [c.content if hasattr(c, "content") else c["content"] for c in chunks]
        ids = [c.id if hasattr(c, "id") else c["id"] for c in chunks]
        metadatas = [
            c.to_metadata() if hasattr(c, "to_metadata") else c.get("metadata", {})
            for c in chunks
        ]

        embeddings = await self.get_embeddings(contents)
        try:
            self.collection.add(
                documents=contents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
        except Exception as e:
            print(f"⚠️ [GraphKnowledgeStore] Lỗi add vectors vào ChromaDB: {e}")

    def load_existing_graph(self) -> nx.DiGraph:
        if os.path.exists(self.graph_file) and os.path.getsize(self.graph_file) > 0:
            try:
                self.graph = nx.read_gml(self.graph_file)
            except Exception:
                self.graph = nx.DiGraph()
        return self.graph