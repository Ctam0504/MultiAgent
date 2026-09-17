#ifndef RAG_PIPELINE_H
#define RAG_PIPELINE_H

#include "data_models.h"
#include "embeddings_service.h"
#include "vector_store.h"
#include "text_processor.h"

typedef struct {
    EmbeddingsService* embeddings_service;
    VectorStore* vector_store;
    TextProcessor* text_processor;
} RAGPipeline;

RAGPipeline* rag_pipeline_create(EmbeddingsService* embeddings_service, VectorStore* vector_store, TextProcessor* text_processor);
void rag_pipeline_destroy(RAGPipeline* pipeline);

QueryResult rag_pipeline_handle_query(RAGPipeline* pipeline, const char* query);

#endif // RAG_PIPELINE_H