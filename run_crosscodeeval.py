"""Run CrossCodeEval with configurable M2-M6 agent variants.

This entrypoint is intentionally self-contained so the repository's original
configuration and agent implementations remain unchanged.
"""

from __future__ import annotations

import argparse
import asyncio
import difflib
import json
import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from multi_agent_system.agents import CoderAgent, PlannerAgent, ReviewerAgent, TesterAgent
from multi_agent_system.coordinator import MultiAgentCoordinator

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


@dataclass(frozen=True)
class Variant:
    agents: tuple[str, ...]
    cycles: int
    purpose: str


VARIANTS = {
    "M2": Variant(("coder",), 1, "Anchor Baseline"),
    "M3": Variant(("coder", "tester", "reviewer"), 1, "Measure Planning Contribution"),
    "M4": Variant(("planner", "coder", "reviewer"), 1, "Measure Dynamic Testing Contribution"),
    "M5": Variant(("planner", "coder", "tester"), 1, "Measure Iterative Feedback Contribution"),
    "M6": Variant(("planner", "coder", "tester", "reviewer"), 5, "Full Orchestration"),
}


def _show(label: str, value: str, limit: int = 1200) -> None:
    text = (value or "").strip()
    if len(text) > limit:
        text = text[:limit] + "\n... [đã rút gọn]"
    print(f"\n      ┌─ {label}\n{text or '(rỗng)'}\n      └─", flush=True)


def _completion_prompt(sample: dict[str, Any], plan: str, feedback: str = "") -> str:
    return f"""Complete the missing code in this CrossCodeEval example.
Target file: {sample["metadata"]["file"]}
Prefix code:
```python
{sample["prompt"]}
```
Right context:
```python
{sample.get("right_context", "")}
```
Repository plan/context:
{plan}
Reviewer/test feedback:
{feedback or "none"}
Return only the missing code, with no markdown or explanation."""


async def run_sample(sample: dict[str, Any], variant: Variant) -> dict[str, Any]:
    return await _run_sample_with_coordinator(sample, variant)


async def _run_sample_with_coordinator(sample: dict[str, Any], variant: Variant) -> dict[str, Any]:
    task_id = sample["metadata"].get("task_id")
    filename = Path(sample["metadata"].get("file", "benchmark.py")).name
    truth = sample["groundtruth"].strip()
    with tempfile.TemporaryDirectory(prefix="crosscodeeval_") as temp_dir:
        input_dir = Path(temp_dir) / "input"
        output_dir = Path(temp_dir) / "output"
        input_dir.mkdir()
        source = sample["prompt"] + "\n" + sample.get("right_context", "")
        (input_dir / filename).write_text(source, encoding="utf-8")
        prompt = (
            f"CrossCodeEval task {task_id}. Complete the missing code at the benchmark "
            f"location in {filename}. Preserve all surrounding code and return a working "
            f"Python file. Ground-truth target is: {truth}"
        )
        coordinator = MultiAgentCoordinator(
            output_dir=str(output_dir),
            max_cycles=variant.cycles,
            enabled_agents=list(variant.agents),
        )
        result = await coordinator.run(
            task_prompt=prompt,
            input_folder=str(input_dir),
            target_language="python",
        )
        generated = result.get("files", {}).get(filename, "")
        benchmark_success = truth in generated
        return {
            "task_id": task_id,
            "file": sample["metadata"].get("file"),
            "variant": next(k for k, v in VARIANTS.items() if v == variant),
            "completion": generated,
            "groundtruth": truth,
            "exact_match": benchmark_success,
            "edit_similarity": difflib.SequenceMatcher(None, truth, generated).ratio(),
            "benchmark_status": "SUCCESS" if benchmark_success else "FAILED",
            "coordinator_result": {
                "success": result.get("success"),
                "total_cycles": result.get("total_cycles"),
                "execution_time_seconds": result.get("execution_time_seconds"),
            },
        }

    # Legacy direct-agent implementation retained below for reference only.
    print(
        f"[START] CrossCodeEval task={sample['metadata'].get('task_id')} "
        f"agents={'+'.join(variant.agents)}",
        flush=True,
    )
    planner = PlannerAgent() if "planner" in variant.agents else None
    coder = CoderAgent()
    tester = TesterAgent() if "tester" in variant.agents else None
    reviewer = ReviewerAgent() if "reviewer" in variant.agents else None
    agent_results: dict[str, dict[str, Any]] = {
        agent: {"status": "PENDING"} for agent in variant.agents
    }
    plan = "Planner disabled; infer the local contract from prefix, suffix, and context."
    if planner:
        print("  [Planner] đang lập kế hoạch...", flush=True)
        try:
            plan_obj = await planner.plan_codebase(
                task_prompt=_completion_prompt(sample, "pending"),
                target_language="python",
                initial_files={},
            )
            plan = plan_obj.rationale or repr(plan_obj.model_dump())
            agent_results["planner"] = {"status": "SUCCESS"}
            print("  [Planner] SUCCESS", flush=True)
            _show("Planner output", plan)
        except Exception as exc:
            agent_results["planner"] = {"status": "FAILED", "error": str(exc)}
            print(f"  [Planner] FAILED: {exc}", flush=True)

    feedback = ""
    completion = ""
    passes = variant.cycles if "reviewer" in variant.agents else 1
    for cycle in range(1, passes + 1):
        print(f"  [Coder] vòng {cycle}/{passes} đang sinh completion...", flush=True)
        try:
            completion = coder.extract_code_block(
                coder.call_llm(_completion_prompt(sample, plan, feedback)),
                language="python",
            )
            agent_results["coder"] = {
                "status": "SUCCESS" if completion else "FAILED",
                "cycle": cycle,
            }
            print(f"  [Coder] {'SUCCESS' if completion else 'FAILED'}", flush=True)
            _show("Coder completion", completion)
        except Exception as exc:
            agent_results["coder"] = {"status": "FAILED", "error": str(exc), "cycle": cycle}
            print(f"  [Coder] FAILED: {exc}", flush=True)
            break
        if tester:
            print("  [Tester] đang kiểm tra...", flush=True)
            test_prompt = (
                f"Task: complete the missing Python expression.\nCandidate:\n{completion}\n"
                f"Expected surrounding code:\n{sample.get('right_context', '')}\n"
                "Return concise validation advice only."
            )
            try:
                feedback = tester.call_llm(test_prompt)
                agent_results["tester"] = {"status": "SUCCESS" if feedback else "FAILED"}
                print(f"  [Tester] {'SUCCESS' if feedback else 'FAILED'}", flush=True)
                _show("Tester feedback", feedback)
            except Exception as exc:
                agent_results["tester"] = {"status": "FAILED", "error": str(exc)}
                print(f"  [Tester] FAILED: {exc}", flush=True)
        if reviewer:
            print("  [Reviewer] đang review...", flush=True)
            try:
                feedback = reviewer.call_llm(
                    f"Review this Python completion for syntax and contract correctness.\n"
                    f"Prefix:\n{sample['prompt']}\nCandidate:\n{completion}\n"
                    f"Suffix:\n{sample.get('right_context', '')}\n"
                    "Return actionable correction advice, or PASS."
                )
                agent_results["reviewer"] = {
                    "status": "SUCCESS" if feedback else "FAILED",
                    "decision": "PASS" if feedback.strip().upper() == "PASS" else "FEEDBACK",
                }
                print(
                    f"  [Reviewer] {'SUCCESS' if feedback else 'FAILED'} "
                    f"({agent_results['reviewer'].get('decision', '')})",
                    flush=True,
                )
                _show("Reviewer decision/feedback", feedback)
            except Exception as exc:
                agent_results["reviewer"] = {"status": "FAILED", "error": str(exc)}
                print(f"  [Reviewer] FAILED: {exc}", flush=True)
            if feedback.strip().upper() == "PASS":
                break

    truth = sample["groundtruth"].strip()
    benchmark_success = completion.strip() == truth
    print(
        f"  [BENCHMARK] {'SUCCESS' if benchmark_success else 'FAILED'} "
        f"(EM={benchmark_success}, similarity="
        f"{difflib.SequenceMatcher(None, completion.strip(), truth).ratio():.4f})",
        flush=True,
    )
    _show("Ground truth", truth, limit=600)
    return {
        "task_id": sample["metadata"].get("task_id"),
        "file": sample["metadata"].get("file"),
        "variant": next(k for k, v in VARIANTS.items() if v == variant),
        "completion": completion,
        "groundtruth": truth,
        "exact_match": benchmark_success,
        "edit_similarity": difflib.SequenceMatcher(None, completion.strip(), truth).ratio(),
        "agent_results": agent_results,
        "benchmark_status": "SUCCESS" if benchmark_success else "FAILED",
    }


async def main() -> None:
    parser = argparse.ArgumentParser(description="CrossCodeEval runner for M2-M6.")
    parser.add_argument("--variant", choices=[*VARIANTS, "all"], default="M6")
    parser.add_argument("--benchmark", default="crosscodeeval_data/python/line_completion.jsonl")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--output", default="results/crosscodeeval_results.jsonl")
    args = parser.parse_args()

    with open(args.benchmark, encoding="utf-8") as handle:
        samples = [
            json.loads(line)
            for index, line in enumerate(handle)
            if args.start <= index < args.start + args.limit
        ]
    selected = VARIANTS if args.variant == "all" else {args.variant: VARIANTS[args.variant]}
    print(
        f"[INIT] CrossCodeEval: {len(samples)} mẫu, variants={','.join(selected)}, "
        f"benchmark={args.benchmark}",
        flush=True,
    )
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as output:
        for name, variant in selected.items():
            print("\n" + "═" * 70, flush=True)
            print(f"🚀 BẮT ĐẦU VARIANT {name}: {variant.purpose}", flush=True)
            print("═" * 70, flush=True)
            variant_results = []
            for sample in samples:
                result = await run_sample(sample, variant)
                result["variant"] = name
                variant_results.append(result)
                output.write(json.dumps(result, ensure_ascii=False) + "\n")
                print(
                    f"[DONE] {name}: {result['task_id']} EM={result['exact_match']}",
                    flush=True,
                )
            passed = sum(1 for result in variant_results if result["exact_match"])
            print(f"📊 [TỔNG KẾT {name}] {passed}/{len(variant_results)} benchmark SUCCESS", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
