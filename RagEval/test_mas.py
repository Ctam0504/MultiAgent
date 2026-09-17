import asyncio
import json
import difflib
from pipeline.mas import run_mas_completion

async def test_single_sample():
    benchmark_path = r"line_completion_rg1_unixcoder_cosine_sim.jsonl"
    
    # Đọc ví dụ đầu tiên
    print("Đang đọc mẫu benchmark đầu tiên...")
    with open(benchmark_path, "r", encoding="utf-8") as f:
        first_line = f.readline()
        data = json.loads(first_line)
        
    file_path = data["metadata"]["file"]
    prompt = data["prompt"]
    right_context = data.get("right_context", "")
    crossfile_list = data.get("crossfile_context", {}).get("list", [])
    groundtruth = data["groundtruth"]
    
    print(f"\n📂 File đang xử lý: {file_path}")
    print(f"📊 Độ dài Prompt: {len(prompt)} ký tự")
    print(f"🔗 Số lượng file cross-context liên quan: {len(crossfile_list)}")
    print(f"🎯 Ground Truth: '{groundtruth}'")
    
    print("\n🚀 Bắt đầu chạy MAS (Planner + Coder) với GraphRAG...")
    completion, plan, retrieved_context = await run_mas_completion(
        file_path=file_path,
        prompt=prompt,
        right_context=right_context,
        crossfile_list=crossfile_list,
        groundtruth=groundtruth,
        top_k=2
    )
    
    print("\n--- GRAPHRAG RETRIEVED CONTEXT ---")
    print(retrieved_context[:500] + "\n..." if len(retrieved_context) > 500 else retrieved_context)
    
    print("\n--- PLANNER PLAN ---")
    print(plan)
    
    print("\n--- CODER COMPLETION ---")
    print(f"'{completion}'")
    
    # Tính toán metrics
    em = completion.strip() == groundtruth.strip()
    sim = difflib.SequenceMatcher(None, completion.strip(), groundtruth.strip()).ratio()
    
    print(f"\n✅ Kết quả đánh giá:")
    print(f"  - Exact Match (EM): {em}")
    print(f"  - Edit Similarity: {sim:.4f}")

if __name__ == "__main__":
    asyncio.run(test_single_sample())
