package services;

import models.TextChunk;
import java.util.List;
import java.util.ArrayList;
import java.util.Arrays;

public class EmbeddingService {
    public List<float[]> computeEmbeddings(List<TextChunk> textChunks) {
        List<float[]> embeddings = new ArrayList<>();
        for (TextChunk chunk : textChunks) {
            embeddings.add(computeEmbedding(chunk.getText()));
        }
        return embeddings;
    }

    private float[] computeEmbedding(String text) {
        // Placeholder for actual embedding computation logic
        // For demonstration, returning a dummy embedding
        return new float[]{0.1f, 0.2f, 0.3f, 0.4f};
    }
}