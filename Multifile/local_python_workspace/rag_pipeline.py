from data_models import Query, Document
from text_processor import TextProcessor
from embedding_service import EmbeddingService
from vector_store import VectorStore

class RAGPipeline:
    def __init__(self, embedding_service: EmbeddingService, vector_store: VectorStore):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.text_processor = TextProcessor()

    def process_query(self, query: Query) -> Document:
        try:
            # Process the query text
            processed_query = self.text_processor.process(query.text)

            # Generate embeddings for the processed query
            query_embedding = self.embedding_service.get_embedding(processed_query)

            # Search for relevant documents in the vector store
            relevant_documents = self.vector_store.search(query_embedding)

            # Combine the query and relevant documents
            combined_document = Document(query=query, documents=relevant_documents)

            return combined_document
        except Exception as e:
            raise Exception(f"Error processing query: {e}")