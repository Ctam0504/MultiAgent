package app;

import services.RAGPipelineService;

public class Main {
    public static void main(String[] args) {
        RAGPipelineService ragPipelineService = new RAGPipelineService();
        List<float[]> results = ragPipelineService.processQuery("Your query here");
        // Process the results as needed
    }
}