import asyncio
import json
import argparse
import difflib
import time
import os
from pipeline.mas import run_mas_completion

async def main():
    parser = argparse.ArgumentParser(description="Đánh giá MAS (Planner + Coder) với GraphRAG trên benchmark Line Completion.")
    parser.add_argument("--limit", type=int, default=20, help="Số lượng mẫu cần đánh giá.")
    parser.add_argument("--start", type=int, default=0, help="Chỉ mục bắt đầu.")
    parser.add_argument("--output", type=str, default="evaluation_results.jsonl", help="Đường dẫn file kết quả.")
    parser.add_argument("--benchmark", type=str, default="line_completion_rg1_unixcoder_cosine_sim.jsonl", help="Đường dẫn file benchmark.")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.benchmark):
        print(f"❌ Không tìm thấy file benchmark tại {args.benchmark}")
        return
        
    print(f"📋 Bắt đầu đánh giá từ mẫu {args.start} đến {args.start + args.limit}...")
    print(f"📂 Kết quả sẽ được ghi vào: {args.output}\n")
    
    samples = []
    with open(args.benchmark, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if idx >= args.start and len(samples) < args.limit:
                samples.append((idx, json.loads(line)))
            if len(samples) >= args.limit:
                break
                
    total = len(samples)
    em_count = 0
    total_similarity = 0.0
    
    # Mở file ghi kết quả
    with open(args.output, "w", encoding="utf-8") as out_f:
        pass
        
    start_time = time.time()
    
    for i, (original_idx, data) in enumerate(samples):
        file_path = data["metadata"]["file"]
        prompt = data["prompt"]
        right_context = data.get("right_context", "")
        crossfile_list = data.get("crossfile_context", {}).get("list", [])
        groundtruth = data["groundtruth"]
        task_id = data["metadata"]["task_id"]
        
        print(f"🔄 [{i+1}/{total}] Đang xử lý Sample #{original_idx} (Task ID: {task_id}, File: {file_path})...")
        
        try:
            # Chạy MAS completion pipeline
            completion, plan, retrieved_context = await run_mas_completion(
                file_path=file_path,
                prompt=prompt,
                right_context=right_context,
                crossfile_list=crossfile_list,
                groundtruth=groundtruth,
                top_k=2
            )
            
            # Tính toán metrics
            em = completion.strip() == groundtruth.strip()
            sim = difflib.SequenceMatcher(None, completion.strip(), groundtruth.strip()).ratio()
            
            if em:
                em_count += 1
            total_similarity += sim
            
            print(f"  └─ Coder: '{completion}'")
            print(f"  └─ Truth: '{groundtruth}'")
            print(f"  └─ EM: {em} | Edit Similarity: {sim:.4f}\n")
            
            # Ghi kết quả vào file
            result = {
                "sample_index": original_idx,
                "task_id": task_id,
                "file": file_path,
                "groundtruth": groundtruth,
                "completion": completion,
                "plan": plan,
                "exact_match": em,
                "edit_similarity": sim,
                "retrieved_context_len": len(retrieved_context)
            }
            with open(args.output, "a", encoding="utf-8") as out_f:
                out_f.write(json.dumps(result, ensure_ascii=False) + "\n")
                
        except Exception as e:
            print(f"  ❌ Lỗi khi xử lý mẫu #{original_idx}: {e}\n")
            
    elapsed = time.time() - start_time
    avg_em = (em_count / total) * 100 if total > 0 else 0
    avg_sim = (total_similarity / total) * 100 if total > 0 else 0
    
    print("=" * 50)
    print("📊 KẾT QUẢ ĐÁNH GIÁ TỔNG QUAN:")
    print(f"  - Tổng số mẫu đánh giá: {total}")
    print(f"  - Tỷ lệ Exact Match (EM): {avg_em:.2f}%")
    print(f"  - Edit Similarity trung bình: {avg_sim:.2f}%")
    print(f"  - Thời gian thực hiện: {elapsed:.2f} giây (~{elapsed/total:.2f} giây/mẫu)")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
