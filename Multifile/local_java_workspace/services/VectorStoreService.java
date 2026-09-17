package services;

import models.TextChunk;
import java.util.List;

public class VectorStoreService {
    private EmbeddingService embeddingService;

    public VectorStoreService() {
        this.embeddingService = new EmbeddingService();
    }

    public List<float[]> storeVectors(List<TextChunk> textChunks) {
        return embeddingService.computeEmbeddings(textChunks);
    }

    public float calculateSimilarity(float[] vector1, float[] vector2) {
        if (vector1.length != vector2.length) {
            throw new IllegalArgumentException("Vectors must have the same dimension");
        }

        float dotProduct = 0.0f;
        float norm1 = 0.0f;
        float norm2 = 0.0f;

        for (int i = 0; i < vector1.length; i++) {
            dotProduct += vector1[i] * vector2[i];
            norm1 += vector1[i] * vector1[i];
            norm2 += vector2[i] * vector2[i];
        }

        norm1 = (float) Math.sqrt(norm1);
        norm2 = (float) Math.sqrt(norm2);

        if (norm1 == 0 || norm2 == 0) {
            throw new IllegalArgumentException("Vectors must not be zero vectors");
        }

        return dotProduct / (norm1 * norm2);
    }
}