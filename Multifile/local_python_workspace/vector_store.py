from data_models import Vector, Document
from embedding_service import EmbeddingService

class VectorStore:
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
        self.vectors = {}

    def add_document(self, document: Document):
        if document.id in self.vectors:
            raise ValueError(f"Document with id {document.id} already exists")
        vector = self.embedding_service.get_embedding(document.text)
        self.vectors[document.id] = Vector(document.id, vector)

    def get_vector(self, document_id: str) -> Vector:
        if document_id not in self.vectors:
            raise ValueError(f"Document with id {document_id} not found")
        return self.vectors[document_id]

    def update_document(self, document: Document):
        if document.id not in self.vectors:
            raise ValueError(f"Document with id {document.id} not found")
        vector = self.embedding_service.get_embedding(document.text)
        self.vectors[document.id] = Vector(document.id, vector)

    def delete_document(self, document_id: str):
        if document_id not in self.vectors:
            raise ValueError(f"Document with id {document_id} not found")
        del self.vectors[document_id]

    def search(self, query: str, top_k: int = 5) -> list:
        query_vector = self.embedding_service.get_embedding(query)
        scores = [(doc_id, self.vectors[doc_id].similarity(query_vector)) for doc_id in self.vectors]
        scores.sort(key=lambda x: x[1], reverse=True)
        return [self.vectors[doc_id] for doc_id, _ in scores[:top_k]]