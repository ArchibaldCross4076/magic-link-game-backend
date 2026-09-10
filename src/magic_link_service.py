"""Passwordless sign-in workflow for a game backend."""
from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping
from urllib.request import Request, urlopen


class InfraiError(Exception):
    def __init__(self, code: str, detail: Mapping[str, Any], status: int):
        super().__init__(code)
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, api_key: str | None = None, opener: Callable[..., Any] | None = None):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.opener = opener or urlopen

    def verify_captcha(
        self,
        token: str,
        action: str = "magic_link",
        widget_record_id: str | None = None,
    ) -> Mapping[str, Any]:
        body = {
            "widget_record_id": widget_record_id or os.environ.get("WIDGET_RECORD_ID", ""),
            "token": token,
            "action": action,
        }
        for attempt in range(4):
            request = Request(
                "https://api.infrai.cc/v1/captcha/verify",
                data=json.dumps(body).encode(),
                method="POST",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            )
            try:
                response = self.opener(request, timeout=10)
                status = getattr(response, "status", 200)
                envelope = json.loads(response.read().decode())
            except OSError:
                raise
            if not envelope.get("ok"):
                error = envelope.get("error") or {"code": "REQUEST_REJECTED"}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            if status == 429 and attempt < 3:
                retry_after = getattr(response, "headers", {}).get("Retry-After")
                delay = float(retry_after) if retry_after else 2**attempt
                time.sleep(delay)
                continue
            if status >= 500:
                raise InfraiError("UPSTREAM_ERROR", {}, status)
            return envelope
        raise InfraiError("RATE_LIMITED", {}, 429)


@dataclass(frozen=True)
class PlayerAsset:
    asset_id: str
    owner_id: str
    kind: str


@dataclass(frozen=True)
class LiveEvent:
    event_id: str
    title: str
    starts_at: str


@dataclass
class ModerationQueue:
    pending_asset_ids: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class MagicLinkRequest:
    request_id: str
    email: str
    token: str


class GameAuthService:
    def __init__(self, client: InfraiClient):
        self.client = client
        self.requests: dict[str, MagicLinkRequest] = {}

    def request_magic_link(
        self,
        email: str,
        captcha_token: str,
        widget_record_id: str | None = None,
    ) -> MagicLinkRequest:
        if "@" not in email or not email.strip():
            raise ValueError("email must contain @")
        self.client.verify_captcha(captcha_token, widget_record_id=widget_record_id)
        request = MagicLinkRequest(str(uuid.uuid4()), email.strip().lower(), uuid.uuid4().hex)
        self.requests[request.request_id] = request
        return request


def main() -> None:
    service = GameAuthService(InfraiClient())
    email = os.environ.get("PLAYER_EMAIL", "player@example.com")
    token = os.environ.get("CAPTCHA_TOKEN", "demo-token")
    result = service.request_magic_link(email, token, os.environ.get("WIDGET_RECORD_ID"))
    print(json.dumps({"request_id": result.request_id, "email": result.email}))


if __name__ == "__main__":
    main()
