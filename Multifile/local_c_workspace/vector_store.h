#ifndef VECTOR_STORE_H
#define VECTOR_STORE_H

#include "data_models.h"
#include "embeddings_service.h"

typedef struct VectorStore {
    // Define the structure of the Vector Store
} VectorStore;

VectorStore* vector_store_create();
void vector_store_destroy(VectorStore* store);

void vector_store_add(VectorStore* store, const Embedding* embedding);
void vector_store_remove(VectorStore* store, const Embedding* embedding);

float vector_store_similarity(const VectorStore* store, const Embedding* query, const Embedding* candidate);

#endif // VECTOR_STORE_H