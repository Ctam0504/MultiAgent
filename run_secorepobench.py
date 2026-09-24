"""Run SecRepoBench without modifying checked-in files or benchmark data."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
import subprocess
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


def _prompt(item: dict[str, Any], plan: str, feedback: str = "") -> str:
    return f"""Repair the vulnerable function in {item["changed_file"]}.
Project: {item["project_name"]}; CWE: {item.get("CWE_ID")}
Masked function:
```c
{item["masked_func"]}
```
Plan: {plan}
Feedback: {feedback or "none"}
Return only the complete replacement function."""


async def run_item(item: dict[str, Any], variant: Variant, work_root: Path) -> dict[str, Any]:
    return await _run_item_with_coordinator(item, variant, work_root)


async def _run_item_with_coordinator(
    item: dict[str, Any], variant: Variant, work_root: Path
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="secorepobench_") as temp_dir:
        input_dir = Path(temp_dir) / "input"
        output_dir = Path(temp_dir) / "output"
        input_dir.mkdir()
        filename = Path(item["changed_file"]).name
        (input_dir / filename).write_text(item["masked_func"], encoding="utf-8")
        prompt = (
            f"SecRepoBench item {item['id']} from {item['project_name']}. Repair CWE-"
            f"{item.get('CWE_ID')} in {filename}. Preserve the function signature and "
            "produce a secure, compilable C implementation."
        )
        coordinator = MultiAgentCoordinator(
            output_dir=str(output_dir),
            max_cycles=variant.cycles,
            enabled_agents=list(variant.agents),
        )
        result = await coordinator.run(
            task_prompt=prompt,
            input_folder=str(input_dir),
            target_language="c",
        )
        generated = result.get("files", {}).get(filename, "")
        target = work_root / str(item["id"]) / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(generated, encoding="utf-8")
        return {
            "id": item["id"],
            "project_name": item["project_name"],
            "changed_file": item["changed_file"],
            "cwe_id": item.get("CWE_ID"),
            "variant": next(k for k, v in VARIANTS.items() if v == variant),
            "patch": generated,
            "temporary_path": str(target),
            "benchmark_status": "GENERATED" if generated else "FAILED",
            "coordinator_result": {
                "success": result.get("success"),
                "total_cycles": result.get("total_cycles"),
                "execution_time_seconds": result.get("execution_time_seconds"),
            },
        }

    # Legacy direct-agent implementation retained below for reference only.
    print(
        f"[START] SecRepoBench id={item['id']} CWE-{item.get('CWE_ID')} "
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
    plan = "Planner disabled; preserve the function signature and fix the security defect."
    if planner:
        print("  [Planner] đang lập kế hoạch...", flush=True)
        try:
            plan_obj = await planner.plan_codebase(
                task_prompt=_prompt(item, "pending"),
                target_language="c",
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
    patch = ""
    passes = variant.cycles if reviewer else 1
    for cycle in range(1, passes + 1):
        print(f"  [Coder] vòng {cycle}/{passes} đang sinh bản sửa...", flush=True)
        try:
            patch = coder.extract_code_block(
                coder.call_llm(_prompt(item, plan, feedback)), language="c"
            )
            agent_results["coder"] = {
                "status": "SUCCESS" if patch else "FAILED",
                "cycle": cycle,
            }
            print(f"  [Coder] {'SUCCESS' if patch else 'FAILED'}", flush=True)
            _show("Coder patch", patch)
        except Exception as exc:
            agent_results["coder"] = {"status": "FAILED", "error": str(exc), "cycle": cycle}
            print(f"  [Coder] FAILED: {exc}", flush=True)
            break
        if tester:
            print("  [Tester] đang kiểm tra an toàn bộ nhớ...", flush=True)
            try:
                feedback = tester.call_llm(
                    f"Assess this C security fix for memory safety and compilation:\n{patch}"
                )
                agent_results["tester"] = {"status": "SUCCESS" if feedback else "FAILED"}
                print(f"  [Tester] {'SUCCESS' if feedback else 'FAILED'}", flush=True)
                _show("Tester feedback", feedback)
            except Exception as exc:
                agent_results["tester"] = {"status": "FAILED", "error": str(exc)}
                print(f"  [Tester] FAILED: {exc}", flush=True)
        if reviewer:
            print("  [Reviewer] đang review CWE...", flush=True)
            try:
                feedback = reviewer.call_llm(
                    f"Adversarially review this C function repair for CWE-{item.get('CWE_ID')}:\n{patch}\n"
                    "Return PASS or precise corrections."
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

    target = work_root / str(item["id"]) / Path(item["changed_file"]).name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(patch, encoding="utf-8")
    benchmark_status = "GENERATED" if patch else "FAILED"
    print(
        f"  [BENCHMARK] {benchmark_status} "
        "(SecRepoBench data has no expected fixed patch; correctness requires external security tests)",
        flush=True,
    )
    return {
        "id": item["id"],
        "project_name": item["project_name"],
        "changed_file": item["changed_file"],
        "cwe_id": item.get("CWE_ID"),
        "variant": next(k for k, v in VARIANTS.items() if v == variant),
        "patch": patch,
        "temporary_path": str(target),
        "agent_results": agent_results,
        "benchmark_status": benchmark_status,
    }


async def main() -> None:
    parser = argparse.ArgumentParser(description="SecRepoBench runner for M2-M6.")
    parser.add_argument("--variant", choices=[*VARIANTS, "all"], default="M6")
    parser.add_argument("--benchmark", default="secorepobench_data.json")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--output", default="results/secorepobench_results.jsonl")
    parser.add_argument("--work-dir", default=None)
    args = parser.parse_args()

    with open(args.benchmark, encoding="utf-8") as handle:
        records = json.load(handle)[args.start : args.start + args.limit]
    selected = VARIANTS if args.variant == "all" else {args.variant: VARIANTS[args.variant]}
    print(
        f"[INIT] SecRepoBench: {len(records)} mẫu, variants={','.join(selected)}, "
        f"benchmark={args.benchmark}",
        flush=True,
    )
    work_dir = Path(args.work_dir) if args.work_dir else Path(tempfile.mkdtemp(prefix="secorepo_"))
    work_dir.mkdir(parents=True, exist_ok=True)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as output:
        for name, variant in selected.items():
            print("\n" + "═" * 70, flush=True)
            print(f"🚀 BẮT ĐẦU VARIANT {name}: {variant.purpose}", flush=True)
            print("═" * 70, flush=True)
            variant_results = []
            for item in records:
                result = await run_item(item, variant, work_dir)
                result["variant"] = name
                variant_results.append(result)
                output.write(json.dumps(result, ensure_ascii=False) + "\n")
                print(f"[DONE] {name}: {item['id']} generated", flush=True)
            generated = sum(1 for result in variant_results if result["benchmark_status"] == "GENERATED")
            print(
                f"📊 [TỔNG KẾT {name}] {generated}/{len(variant_results)} patch generated "
                "(chưa phải xác nhận security pass)",
                flush=True,
            )


if __name__ == "__main__":
    asyncio.run(main())
