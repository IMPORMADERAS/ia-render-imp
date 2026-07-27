from __future__ import annotations

import argparse
import concurrent.futures
import io
import json
import random
import string
import time
from dataclasses import dataclass
from typing import Any, Callable

import httpx
from PIL import Image


@dataclass
class UserSession:
    email: str
    password: str
    cookies: dict[str, str]


ActionFn = Callable[..., dict[str, Any]]


def _parse_cookie_header(raw: str) -> dict[str, str]:
    cookies: dict[str, str] = {}
    for part in str(raw or "").split(";"):
        item = part.strip()
        if not item or "=" not in item:
            continue
        key, value = item.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key:
            cookies[key] = value
    return cookies


def _validate_cookie_session(base_url: str, cookies: dict[str, str], timeout: float) -> None:
    with httpx.Client(base_url=base_url, timeout=timeout, cookies=cookies, follow_redirects=True) as client:
        response = client.get("/auth/me")
    if response.status_code >= 400:
        body = (response.text or "").strip()
        if len(body) > 220:
            body = body[:220] + "..."
        raise SystemExit(
            "Cookie de usuario invalida o expirada. Inicia sesion en /studio, copia SOLO iaimp_session y vuelve a ejecutar. "
            f"Status={response.status_code} body={body}"
        )


def _random_suffix(length: int = 8) -> str:
    alphabet = string.ascii_lowercase + string.digits
    return "".join(random.choice(alphabet) for _ in range(length))


def _png_bytes() -> bytes:
    image = Image.new("RGB", (256, 256), (16, 53, 34))
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()


def _fake_mp4_bytes() -> bytes:
    return b"\x00\x00\x00\x18ftypmp42IA-IMP-benchmark-video"


def _register_user(base_url: str, password: str, timeout: float, email_prefix: str) -> UserSession:
    suffix = _random_suffix()
    email = f"{email_prefix}-{suffix}@example.com"
    payload = {
        "first_name": "Load",
        "last_name": "Tester",
        "email": email,
        "password": password,
        "password_confirm": password,
    }

    with httpx.Client(base_url=base_url, timeout=timeout, follow_redirects=True) as client:
        response = client.post("/auth/register", json=payload)
        response.raise_for_status()
        cookies = dict(client.cookies)

    return UserSession(email=email, password=password, cookies=cookies)


def _post_json(base_url: str, path: str, payload: dict[str, Any], cookies: dict[str, str], timeout: float) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        with httpx.Client(base_url=base_url, timeout=timeout, cookies=cookies, follow_redirects=True) as client:
            response = client.post(path, json=payload)
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        return {
            "path": path,
            "status": int(response.status_code),
            "elapsed_ms": elapsed_ms,
            "ok": response.status_code < 500,
        }
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        return {
            "path": path,
            "status": 0,
            "elapsed_ms": elapsed_ms,
            "ok": False,
            "error": str(exc),
        }


def _post_form(
    base_url: str,
    path: str,
    data: dict[str, Any],
    files: dict[str, tuple[str, bytes, str]] | None,
    cookies: dict[str, str],
    timeout: float,
) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        with httpx.Client(base_url=base_url, timeout=timeout, cookies=cookies, follow_redirects=True) as client:
            response = client.post(path, data=data, files=files)
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        return {
            "path": path,
            "status": int(response.status_code),
            "elapsed_ms": elapsed_ms,
            "ok": response.status_code < 500,
        }
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        return {
            "path": path,
            "status": 0,
            "elapsed_ms": elapsed_ms,
            "ok": False,
            "error": str(exc),
        }


def _action_recharge(base_url: str, session: UserSession, timeout: float) -> dict[str, Any]:
    amount = random.choice([5000, 10000, 20000, 50000])
    return _post_json(base_url, "/auth/recharge", {"amount_cop": amount}, session.cookies, timeout)


def _action_chat(base_url: str, session: UserSession, timeout: float) -> dict[str, Any]:
    payload = {
        "message": random.choice(
            [
                "que es impormaderas",
                "en que ciudad estan",
                "cual es la pagina web de impormaderas",
                "lineas de atencion",
            ]
        ),
        "context": "prueba de carga mixta",
    }
    return _post_json(base_url, "/chat/message", payload, session.cookies, timeout)


def _action_render_text(base_url: str, session: UserSession, timeout: float) -> dict[str, Any]:
    data = {
        "prompt": "fachada moderna minimalista con madera y vidrio",
        "style": "editorial",
        "lighting_mode": "afternoon",
        "quality": "fast",
        "steps": "4",
        "guidance_scale": "6.5",
    }
    return _post_form(base_url, "/jobs/render-text", data, None, session.cookies, timeout)


def _action_render_image(base_url: str, session: UserSession, timeout: float, png_payload: bytes) -> dict[str, Any]:
    data = {
        "prompt": "interior arquitectonico con paneleria de madera",
        "style": "editorial",
        "lighting_mode": "morning",
        "quality": "fast",
        "steps": "4",
        "guidance_scale": "6.0",
    }
    files = {
        "file": ("input.png", png_payload, "image/png"),
    }
    return _post_form(base_url, "/jobs/render", data, files, session.cookies, timeout)


def _action_music(base_url: str, session: UserSession, timeout: float) -> dict[str, Any]:
    data = {
        "mode": "instrumental",
        "genre": "cinematic electronic",
        "mood": "uplifting",
        "instruments": "synth,bass,drums",
        "user_taste": "clear mix",
        "duration_seconds": "8",
    }
    return _post_form(base_url, "/music/generate", data, None, session.cookies, timeout)


def _action_animate(base_url: str, session: UserSession, timeout: float, png_payload: bytes) -> dict[str, Any]:
    data = {
        "prompt": "camera pan, natural breeze",
        "model": "wan-video/wan-2.2-i2v-fast",
        "duration_seconds": "3",
    }
    files = {
        "file": ("input.png", png_payload, "image/png"),
    }
    return _post_form(base_url, "/animate", data, files, session.cookies, timeout)


def _action_influencer(base_url: str, session: UserSession, timeout: float, png_payload: bytes, mp4_payload: bytes) -> dict[str, Any]:
    data = {
        "instruction_prompt": "hablar mirando a camara con tono corporativo",
        "character_mode": "original",
        "resolution": "720p",
        "target_fps": "24",
        "turbo": "false",
        "consent_confirmed": "true",
    }
    files = {
        "reference_image": ("reference.png", png_payload, "image/png"),
        "source_video": ("source.mp4", mp4_payload, "video/mp4"),
    }
    return _post_form(base_url, "/influencer/create", data, files, session.cookies, timeout)


def main() -> None:
    parser = argparse.ArgumentParser(description="Mixed business load test for IA-IMP")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Base URL of the API")
    parser.add_argument("--users", type=int, default=20, help="Number of synthetic users to create")
    parser.add_argument("--requests", type=int, default=200, help="Number of mixed requests to execute")
    parser.add_argument("--concurrency", type=int, default=20, help="Concurrent request workers")
    parser.add_argument("--timeout", type=float, default=15.0, help="Per-request timeout in seconds")
    parser.add_argument("--password", default="CargaSegura123!", help="Password for synthetic users")
    parser.add_argument("--email-prefix", default="iaimp-load", help="Email prefix for synthetic users")
    parser.add_argument(
        "--cookie",
        default="",
        help="Optional cookie header for an existing logged-in user, e.g. iaimp_session=...",
    )
    parser.add_argument("--include-animate", action="store_true", help="Include image-to-video requests")
    parser.add_argument("--include-influencer", action="store_true", help="Include influencer requests (use benchmark mode)")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    timeout = max(1.0, float(args.timeout))
    users_total = max(1, int(args.users))
    requests_total = max(1, int(args.requests))
    concurrency = max(1, int(args.concurrency))
    png_payload = _png_bytes()
    mp4_payload = _fake_mp4_bytes()

    sessions: list[UserSession] = []
    cookie_session = _parse_cookie_header(args.cookie)
    if cookie_session:
        _validate_cookie_session(base_url, cookie_session, timeout)
        sessions.append(UserSession(email="existing-session", password="", cookies=cookie_session))
    else:
        for _ in range(users_total):
            sessions.append(_register_user(base_url, args.password, timeout, args.email_prefix))

    actions: list[ActionFn] = [_action_recharge, _action_chat, _action_render_text, _action_render_image, _action_music]
    if args.include_animate:
        actions.append(_action_animate)
    if args.include_influencer:
        actions.append(_action_influencer)

    def _worker() -> dict[str, Any]:
        session = random.choice(sessions)
        action = random.choice(actions)
        if action is _action_render_image:
            return action(base_url, session, timeout, png_payload)
        if action is _action_animate:
            return action(base_url, session, timeout, png_payload)
        if action is _action_influencer:
            return action(base_url, session, timeout, png_payload, mp4_payload)
        return action(base_url, session, timeout)

    results: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(_worker) for _ in range(requests_total)]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    success = sum(1 for item in results if item.get("ok"))
    failures = requests_total - success
    avg_ms = sum(float(item.get("elapsed_ms") or 0) for item in results) / max(1, requests_total)
    p95_index = max(0, min(len(results) - 1, int(len(results) * 0.95) - 1))
    p95_ms = sorted(float(item.get("elapsed_ms") or 0) for item in results)[p95_index]

    status_counts: dict[str, int] = {}
    path_counts: dict[str, int] = {}
    for item in results:
        status_key = str(item.get("status") or 0)
        path_key = str(item.get("path") or "")
        status_counts[status_key] = status_counts.get(status_key, 0) + 1
        path_counts[path_key] = path_counts.get(path_key, 0) + 1

    print(
        json.dumps(
            {
                "base_url": base_url,
                "users": users_total,
                "session_mode": "cookie" if cookie_session else "synthetic-users",
                "requests": requests_total,
                "concurrency": concurrency,
                "include_animate": bool(args.include_animate),
                "include_influencer": bool(args.include_influencer),
                "success": success,
                "failures": failures,
                "avg_ms": round(avg_ms, 2),
                "p95_ms": round(p95_ms, 2),
                "status_counts": status_counts,
                "path_counts": path_counts,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
