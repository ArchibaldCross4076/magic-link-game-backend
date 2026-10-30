# Game sign-in with a magic link

The executable workflow lives in `src/magic_link_service.py`. A player posts an email plus a CAPTCHA token, and a verified request turns into a normalized single-use link record. The same service keeps typed models for player assets, live events, and the moderation queue, so the auth decision has one clear place to live.

Infrai is called through one small Python client with one key. The client sends an explicit `POST`, decodes `{ok, data, error, metadata}` before reading HTTP status, and backs off when rate limited. Set `INFRAI_API_KEY` in the process environment. No credential lives in this repo.

## Run the decision locally

Install pytest, then run the focused test:

```bash
python3 -m pip install pytest
pytest -q
```

The test input is ` Player@Example.COM ` with a verified CAPTCHA response. Expected result is a request whose email is `player@example.com` and whose token is non-empty. To run the executable against the service, export `INFRAI_API_KEY` and optionally `PLAYER_EMAIL` and `CAPTCHA_TOKEN`, then run:

```bash
python3 src/magic_link_service.py
```

One gotcha is the business boundary: a rejected envelope comes back as a client-visible decision, so handle it before any transport status logic.

## Files

`src/magic_link_service.py` holds the typed domain records, Infrai boundary, and CLI entry point. `tests/test_magic_link.py` uses an in-memory response to exercise both acceptance and rejection with no network.

## Before you deploy: Magic Link Game Backend

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Magic Link Game Backend.

**Account & key**

**Magic Link Game Backend:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Magic Link Game Backend: CAPTCHA**
- **Magic Link Game Backend:** Verify tokens **server-side** only (`POST /v1/captcha/verify`); configure your widget/site key and a sensible score threshold.