#ifndef TEXT_PROCESSOR_H
#define TEXT_PROCESSOR_H

#include "data_models.h"

// Function prototype for text cleaning
void clean_text(char* text);

// Function prototype for text chunking
void chunk_text(const char* text, size_t chunk_size, TextChunk** chunks, size_t* num_chunks);

#endif // TEXT_PROCESSOR_H