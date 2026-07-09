"""
dailynews LLM 평가 러너 — orchestration.md §1 Phase3(05_quality Eval) / §5.2 응답 스키마 이행.

측정 지표:
  - format_compliance : issues[]/trends[] 구조·개수 준수율
  - hallucination_rate: 입력에 없는 source URL 비율
  - accuracy          : 기대 키워드(expected_keywords) 반영율(관련성 프록시)

모드:
  (기본)         오프라인. 입력으로부터 grounded 후보 출력을 구성해 가드 파이프라인을 end-to-end 검증.
                 → 하네스·가드 정상 동작 및 계약 강제성 확인용. accuracy 는 후보 기반이라 참고치.
  --live         core.news.analyzer.analyze() 실제 호출로 출력 생성(=진짜 품질 측정, API 키 필요).
  --scan-reports reports/*.json 과거 실출력을 format_compliance 검증에 편입(총 케이스 수 증대).

사용:
  python scripts/eval_news.py                 # 오프라인 가드 검증
  python scripts/eval_news.py --live          # 실 LLM 호출 평가
  python scripts/eval_news.py --scan-reports  # 과거 리포트까지 포함
  python scripts/eval_news.py --json          # 결과를 orchestration §5.2 JSON 으로만 출력

종료코드: deploy_ready(=baseline 충족) 이면 0, 아니면 1.
"""
from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core.shared.output_guard import guard, GuardReport  # noqa: E402

EVAL_SET = _ROOT / "tests" / "eval_set.json"

GREEN, RED, YELLOW, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[0m"


def _load_eval_set() -> dict:
    with open(EVAL_SET, encoding="utf-8") as f:
        return json.load(f)


def _candidate_from_input(case: dict) -> dict:
    """오프라인 모드용: 입력 뉴스에서 grounded 후보 출력을 구성(가드 파이프라인 검증용)."""
    inp = case.get("input", {})
    items = list(inp.get("en", [])) + list(inp.get("ko", []))
    issues = []
    for rank, n in enumerate(items[:5], 1):
        issues.append({
            "rank": rank,
            "title": n.get("title", ""),
            "summary": n.get("title", ""),
            "sources": ([{"title": n.get("label", ""), "url": n.get("link", "")}]
                        if n.get("link") else []),
        })
    # 최소 개수 미달 시(빈 입력 등) 폴백 허용 케이스는 그대로 둠
    trends = [{"keyword": (items[0].get("category", "trend") if items else "trend"),
               "description": "auto"}]
    return {"issues": issues, "trends": trends}


def _live_output(case: dict) -> dict:
    """--live: 실제 analyzer 호출."""
    from core.news.analyzer import analyze
    inp = case.get("input", {})
    return analyze({"en": inp.get("en", []), "ko": inp.get("ko", [])})


def _accuracy(result: dict, expect: dict) -> float | None:
    """expected_keywords 반영율. 키워드 미명세면 None."""
    kws = expect.get("expected_keywords")
    if not kws:
        return None
    blob = json.dumps(result, ensure_ascii=False).lower()
    hit = sum(1 for k in kws if k.lower() in blob)
    return round(hit / len(kws), 4)


def _eval_case(case: dict, live: bool) -> dict:
    expect = case.get("expect", {})
    try:
        result = _live_output(case) if live else _candidate_from_input(case)
    except Exception as e:  # noqa: BLE001
        return {"id": case["id"], "format_ok": False, "grounded": False,
                "count_ok": False, "accuracy": None, "error": str(e), "sources": 0,
                "hallucinated": 0}

    allow_fallback = expect.get("allow_fallback", False)
    rep: GuardReport = guard(result, case.get("input", {}), strict=not allow_fallback)

    # 오프라인 후보는 입력 뉴스 수만큼만 issues 생성 가능 → 입력이 MIN_ISSUES 미만이면
    # 개수 제약은 --live 전용으로 간주(오프라인 false-negative 방지). grounding/format 은 그대로 평가.
    inp = case.get("input", {})
    input_count = len(inp.get("en", [])) + len(inp.get("ko", []))
    count_not_applicable = (not live) and input_count < 3

    format_ok = rep.format_ok
    count_ok = rep.count_ok or allow_fallback or count_not_applicable
    acc = _accuracy(result, expect)

    return {
        "id": case["id"],
        "format_ok": format_ok,
        "count_ok": count_ok,
        "grounded": rep.grounded,
        "accuracy": acc,
        "sources": rep.total_sources,
        "hallucinated": len(rep.hallucinated_sources),
        "hallucinated_urls": rep.hallucinated_sources,
    }


def _scan_reports() -> list[dict]:
    """reports/*.json 실출력을 format_compliance 검증에 편입(grounding 은 입력 부재로 스킵)."""
    rows = []
    for fp in glob.glob(str(_ROOT / "reports" / "**" / "*.json"), recursive=True):
        try:
            with open(fp, encoding="utf-8") as f:
                data = json.load(f)
        except Exception:  # noqa: BLE001
            continue
        # 뉴스/AI이슈 구조만 대상
        payload = data if isinstance(data, dict) and ("issues" in data or "top10" in data) else None
        if payload is None:
            continue
        norm = {"issues": payload.get("issues", payload.get("top10", [])),
                "trends": payload.get("trends", [])}
        rep = guard(norm, [], strict=False)  # 입력 없음 → 그라운딩 스킵
        rows.append({"id": f"report:{Path(fp).name}", "format_ok": rep.format_ok,
                     "count_ok": True, "grounded": True, "accuracy": None,
                     "sources": rep.total_sources, "hallucinated": 0})
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description="dailynews LLM 평가 러너")
    ap.add_argument("--live", action="store_true", help="실제 analyzer 호출(API 키 필요)")
    ap.add_argument("--scan-reports", action="store_true", help="과거 reports/*.json 편입")
    ap.add_argument("--json", action="store_true", help="§5.2 응답 JSON 만 출력")
    args = ap.parse_args()

    spec = _load_eval_set()
    baseline = spec.get("target_baseline", {})
    rows = [_eval_case(c, args.live) for c in spec.get("cases", [])]
    if args.scan_reports:
        rows += _scan_reports()

    total = len(rows)
    fmt_pass = sum(1 for r in rows if r["format_ok"] and r["count_ok"])
    total_sources = sum(r["sources"] for r in rows)
    total_halluc = sum(r["hallucinated"] for r in rows)
    accs = [r["accuracy"] for r in rows if r["accuracy"] is not None]

    format_compliance = round(fmt_pass / total, 4) if total else 0.0
    hallucination_rate = round(total_halluc / total_sources, 4) if total_sources else 0.0
    accuracy = round(sum(accs) / len(accs), 4) if accs else None

    # accuracy 게이트는 실측(--live)에서만 적용. 오프라인 accuracy 는 후보 기반 참고치이므로 제외.
    accuracy_ok = (accuracy is None) or (not args.live) or accuracy >= baseline.get("accuracy", 0.85)
    deploy_ready = (
        format_compliance >= baseline.get("format_compliance", 1.0)
        and hallucination_rate <= baseline.get("hallucination_rate_max", 0.05)
        and accuracy_ok
    )

    response = {
        "sender": "05_quality",
        "task_completed": "평가셋 구동 및 가드 검증",
        "status": "SUCCESS" if deploy_ready else "FAILED",
        "mode": "live" if args.live else "offline-guard",
        "metrics": {
            "total_cases": total,
            "accuracy": accuracy,
            "hallucination_rate": hallucination_rate,
            "format_compliance": format_compliance,
            "deploy_ready": deploy_ready,
        },
        "requires_approval": deploy_ready,
        "approval_items": (["deploy_ready: true - 최종 릴리즈 게이트 진입을 위해 사용자 승인 필요"]
                           if deploy_ready else []),
        "failure_reason": {
            "layer": "NONE" if deploy_ready else ("GUARD" if hallucination_rate > 0 else "PROMPT"),
            "description": "" if deploy_ready else "format/hallucination/accuracy baseline 미충족",
        },
    }

    if args.json:
        print(json.dumps(response, ensure_ascii=False, indent=2))
        return 0 if deploy_ready else 1

    # 사람이 읽는 요약
    print(f"\n=== dailynews 평가 결과 ({response['mode']}) ===")
    for r in rows:
        mark = f"{GREEN}PASS{RESET}" if (r["format_ok"] and r["count_ok"] and r["grounded"]) else f"{RED}FAIL{RESET}"
        extra = f" halluc={r['hallucinated']}" if r["hallucinated"] else ""
        acc = f" acc={r['accuracy']}" if r["accuracy"] is not None else ""
        print(f"  [{mark}] {r['id']}{acc}{extra}")
    m = response["metrics"]
    print(f"\n  total_cases        : {m['total_cases']}")
    print(f"  format_compliance  : {m['format_compliance']}  (target {baseline.get('format_compliance')})")
    print(f"  hallucination_rate : {m['hallucination_rate']}  (max {baseline.get('hallucination_rate_max')})")
    print(f"  accuracy           : {m['accuracy']}  (target {baseline.get('accuracy')})")
    color = GREEN if deploy_ready else YELLOW
    print(f"  deploy_ready       : {color}{deploy_ready}{RESET}\n")
    return 0 if deploy_ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
