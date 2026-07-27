from __future__ import annotations

import argparse
import concurrent.futures
import json
import random
import time
from typing import Any

import httpx


ROUTES = {
    "health": "/admin-api/infra/health",
    "cutover": "/admin-api/infra/cutover",
    "consistency": "/admin-api/infra/consistency",
    "metrics": "/admin-api/infra/metrics",
}


def _pick_route() -> str:
    weighted = [
        (ROUTES["health"], 4),
        (ROUTES["metrics"], 4),
        (ROUTES["cutover"], 1),
        (ROUTES["consistency"], 1),
    ]
    pool: list[str] = []
    for route, weight in weighted:
        pool.extend([route] * weight)
    return random.choice(pool)


def _one_request(base_url: str, cookie_header: str | None, timeout: float) -> dict[str, Any]:
    route = _pick_route()
    started = time.perf_counter()
    headers = {}
    if cookie_header:
        headers["Cookie"] = cookie_header
    try:
        with httpx.Client(base_url=base_url, timeout=timeout, headers=headers, follow_redirects=True) as client:
            response = client.get(route)
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        return {
            "route": route,
            "status": int(response.status_code),
            "elapsed_ms": elapsed_ms,
            "ok": 200 <= response.status_code < 400,
        }
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        return {
            "route": route,
            "status": 0,
            "elapsed_ms": elapsed_ms,
            "ok": False,
            "error": str(exc),
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke load test for admin infra endpoints")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Base URL of the API")
    parser.add_argument("--cookie", default="", help="Optional admin session cookie header, e.g. iaimp_admin_session=...")
    parser.add_argument("--requests", type=int, default=100, help="Total number of requests")
    parser.add_argument("--concurrency", type=int, default=20, help="Number of concurrent workers")
    parser.add_argument("--timeout", type=float, default=10.0, help="Per-request timeout in seconds")
    args = parser.parse_args()

    total = max(1, int(args.requests))
    concurrency = max(1, int(args.concurrency))
    results: list[dict[str, Any]] = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [
            executor.submit(_one_request, args.base_url.rstrip("/"), args.cookie.strip() or None, float(args.timeout))
            for _ in range(total)
        ]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    success = sum(1 for item in results if item.get("ok"))
    failures = total - success
    avg_ms = sum(float(item.get("elapsed_ms") or 0) for item in results) / max(1, total)
    p95_index = max(0, min(len(results) - 1, int(len(results) * 0.95) - 1))
    p95_ms = sorted(float(item.get("elapsed_ms") or 0) for item in results)[p95_index]

    by_status: dict[str, int] = {}
    for item in results:
        key = str(item.get("status") or 0)
        by_status[key] = by_status.get(key, 0) + 1

    auth_failures = int(by_status.get("401", 0)) + int(by_status.get("403", 0))
    hint = ""
    if auth_failures == total:
        hint = "Todas las respuestas fueron 401/403. Revisa que --cookie use iaimp_admin_session real."
    elif auth_failures > 0:
        hint = "Se detectaron respuestas 401/403. Verifica expiración o formato de la cookie."

    print(json.dumps(
        {
            "base_url": args.base_url,
            "requests": total,
            "concurrency": concurrency,
            "success": success,
            "failures": failures,
            "auth_failures": auth_failures,
            "avg_ms": round(avg_ms, 2),
            "p95_ms": round(p95_ms, 2),
            "status_counts": by_status,
            "hint": hint,
        },
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
