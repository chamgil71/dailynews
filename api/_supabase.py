"""Supabase REST API 공통 헬퍼 (서버사이드 전용 — service key 사용)."""
import os
import requests

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://syxpwvmniwzohmxmvlyl.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")


def _h(extra: dict | None = None) -> dict:
    if not SUPABASE_KEY:
        raise EnvironmentError(
            "SUPABASE_SERVICE_KEY 환경변수가 비어 있습니다. "
            "Vercel 대시보드 → Project Settings → Environment Variables에서 추가하세요."
        )
    h = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }
    if extra:
        h.update(extra)
    return h


def sb_get(table: str, params: dict | None = None) -> list[dict]:
    r = requests.get(f"{SUPABASE_URL}/rest/v1/{table}",
                     headers=_h(), params=params or {}, timeout=10)
    r.raise_for_status()
    return r.json()


def sb_insert(table: str, data: dict) -> dict:
    r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}",
                      headers=_h({"Prefer": "return=representation"}),
                      json=data, timeout=10)
    r.raise_for_status()
    result = r.json()
    return result[0] if isinstance(result, list) and result else result


def sb_upsert(table: str, data: dict, on_conflict: str) -> dict:
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=_h({"Prefer": "resolution=merge-duplicates,return=representation",
                     "on-conflict": on_conflict}),
        json=data, timeout=10,
    )
    r.raise_for_status()
    result = r.json()
    return result[0] if isinstance(result, list) and result else result


def sb_patch(table: str, col: str, val: str, data: dict) -> list[dict]:
    r = requests.patch(f"{SUPABASE_URL}/rest/v1/{table}",
                       headers=_h({"Prefer": "return=representation"}),
                       params={col: f"eq.{val}"}, json=data, timeout=10)
    r.raise_for_status()
    return r.json()


def sb_delete(table: str, col: str, val: str) -> None:
    r = requests.delete(f"{SUPABASE_URL}/rest/v1/{table}",
                        headers=_h(), params={col: f"eq.{val}"}, timeout=10)
    r.raise_for_status()
