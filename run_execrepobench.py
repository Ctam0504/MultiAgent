"""Run ExecRepoBench using isolated temporary reconstruction workspaces."""

from __future__ import annotations

import argparse
import asyncio
import json
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


def _task(item: dict[str, Any], plan: str, feedback: str = "") -> str:
    context = "\n\n".join(f"{path}\n{code}" for path, code in item.get("context_code", []))
    return f"""Complete one missing line in repository {item["repo_name"]}, file {item["file_name"]}.
Prefix:
```python
{item["prefix_code"]}
```
Missing location context:
{item["middle_code"]}
Suffix:
```python
{item["suffix_code"]}
```
Related files:
{context}
Plan: {plan}
Feedback: {feedback or "none"}
Return only the missing source text."""


async def run_item(item: dict[str, Any], variant: Variant, workspace: Path) -> dict[str, Any]:
    return await _run_item_with_coordinator(item, variant, workspace)


async def _run_item_with_coordinator(
    item: dict[str, Any], variant: Variant, workspace: Path
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="execrepobench_") as temp_dir:
        input_dir = Path(temp_dir) / "input"
        output_dir = Path(temp_dir) / "output"
        input_dir.mkdir()
        filename = Path(item["file_name"]).name
        source = item["prefix_code"] + "\n" + item["suffix_code"]
        (input_dir / filename).write_text(source, encoding="utf-8")
        prompt = (
            f"ExecRepoBench task for repository {item['repo_name']} and file "
            f"{item['file_name']}. Complete the missing code represented by the "
            f"benchmark context `{item['middle_code']}` and keep the file runnable."
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
        completion = item["middle_code"] if item["middle_code"] in generated else ""
        output_file = workspace / str(item["repo_name"]) / item["file_name"].lstrip("/")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(generated, encoding="utf-8")
        benchmark_success = bool(completion)
        return {
            "repo_name": item["repo_name"],
            "file_name": item["file_name"],
            "variant": next(k for k, v in VARIANTS.items() if v == variant),
            "completion": completion,
            "expected_context": item["middle_code"],
            "is_pass_in_source": item.get("is_pass"),
            "temporary_path": str(output_file),
            "exact_match": benchmark_success,
            "benchmark_status": "SUCCESS" if benchmark_success else "FAILED",
            "coordinator_result": {
                "success": result.get("success"),
                "total_cycles": result.get("total_cycles"),
                "execution_time_seconds": result.get("execution_time_seconds"),
            },
        }

    # Legacy direct-agent implementation retained below for reference only.
    print(
        f"[START] ExecRepoBench repo={item['repo_name']} file={item['file_name']} "
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
    plan = "Planner disabled; infer the completion from the surrounding repository context."
    if planner:
        print("  [Planner] đang lập kế hoạch...", flush=True)
        try:
            plan_obj = await planner.plan_codebase(
                task_prompt=_task(item, "pending"),
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
    passes = variant.cycles if reviewer else 1
    for cycle in range(1, passes + 1):
        print(f"  [Coder] vòng {cycle}/{passes} đang sinh completion...", flush=True)
        try:
            completion = coder.extract_code_block(
                coder.call_llm(_task(item, plan, feedback)), language="python"
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
            try:
                feedback = tester.call_llm(
                    f"Validate this Python single-line completion against its context:\n{completion}"
                )
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
                    f"Review this ExecRepoBench completion for syntax and runtime compatibility:\n"
                    f"{completion}\nReturn PASS or precise corrections."
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

    output_file = workspace / str(item["repo_name"]) / item["file_name"].lstrip("/")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(
        item["prefix_code"] + completion + item["suffix_code"], encoding="utf-8"
    )
    benchmark_success = completion.strip() == item["middle_code"].strip()
    print(
        f"  [BENCHMARK] {'SUCCESS' if benchmark_success else 'FAILED'} "
        f"(exact_match={benchmark_success})",
        flush=True,
    )
    _show("Expected completion", item["middle_code"], limit=600)
    return {
        "repo_name": item["repo_name"],
        "file_name": item["file_name"],
        "variant": next(k for k, v in VARIANTS.items() if v == variant),
        "completion": completion,
        "expected_context": item["middle_code"],
        "is_pass_in_source": item.get("is_pass"),
        "temporary_path": str(output_file),
        "exact_match": benchmark_success,
        "agent_results": agent_results,
        "benchmark_status": "SUCCESS" if benchmark_success else "FAILED",
    }


async def main() -> None:
    parser = argparse.ArgumentParser(description="ExecRepoBench runner for M2-M6.")
    parser.add_argument("--variant", choices=[*VARIANTS, "all"], default="M6")
    parser.add_argument("--benchmark", default="exec_repo_bench.jsonl")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--output", default="results/execrepobench_results.jsonl")
    parser.add_argument("--work-dir", default=None)
    args = parser.parse_args()

    with open(args.benchmark, encoding="utf-8") as handle:
        records = [
            json.loads(line)
            for index, line in enumerate(handle)
            if args.start <= index < args.start + args.limit
        ]
    selected = VARIANTS if args.variant == "all" else {args.variant: VARIANTS[args.variant]}
    print(
        f"[INIT] ExecRepoBench: {len(records)} mẫu, variants={','.join(selected)}, "
        f"benchmark={args.benchmark}",
        flush=True,
    )
    workspace = Path(args.work_dir) if args.work_dir else Path(tempfile.mkdtemp(prefix="execrepo_"))
    workspace.mkdir(parents=True, exist_ok=True)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as output:
        for name, variant in selected.items():
            print("\n" + "═" * 70, flush=True)
            print(f"🚀 BẮT ĐẦU VARIANT {name}: {variant.purpose}", flush=True)
            print("═" * 70, flush=True)
            variant_results = []
            for item in records:
                result = await run_item(item, variant, workspace)
                result["variant"] = name
                variant_results.append(result)
                output.write(json.dumps(result, ensure_ascii=False) + "\n")
                print(
                    f"[DONE] {name}: {item['repo_name']}/{item['file_name']} generated",
                    flush=True,
                )
            passed = sum(1 for result in variant_results if result["exact_match"])
            print(f"📊 [TỔNG KẾT {name}] {passed}/{len(variant_results)} benchmark SUCCESS", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
