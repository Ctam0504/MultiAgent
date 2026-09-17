#ifndef EMBEDDINGS_SERVICE_H
#define EMBEDDINGS_SERVICE_H

#include "data_models.h"

// Function prototype for vector embedding
void* embed_vector(const Vector* input_vector, int* output_size);

#endif // EMBEDDINGS_SERVICE_H