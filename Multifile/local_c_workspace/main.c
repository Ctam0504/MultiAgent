#include "rag_pipeline.h"

int main() {
    // Initialize the RAG pipeline
    if (rag_pipeline_init() != 0) {
        fprintf(stderr, "Failed to initialize RAG pipeline\n");
        return 1;
    }

    // Run the RAG pipeline
    if (rag_pipeline_run() != 0) {
        fprintf(stderr, "Failed to run RAG pipeline\n");
        rag_pipeline_cleanup();
        return 1;
    }

    // Clean up the RAG pipeline
    rag_pipeline_cleanup();

    return 0;
}