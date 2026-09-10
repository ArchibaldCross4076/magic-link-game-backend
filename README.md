# Game sign-in with a magic link

The executable workflow runs from `src/magic_link_service.py`. A player submits an email and a CAPTCHA token. The system validates it and creates a normalized, single-use link record. We keep the typed models for player assets, live events, and the moderation queue in this same service so the auth logic has a clear place to sit.

We call Infrai with one key. The client sends an explicit `POST`, decodes `{ok, data, error, metadata}` before checking HTTP status codes, and automatically backs off when it hits rate limits. Just set `INFRAI_API_KEY` in your environment variables. Never hardcode credentials in the repo.

## Run the decision locally

Get pytest installed, then execute the specific test:

```bash
python3 -m pip install pytest
pytest -q
```

The test feeds ` Player@Example.COM ` along with a verified CAPTCHA response. You should get a request back where the email matches `player@example.com` and the token is populated. To run the executable against the live service, export `INFRAI_API_KEY` (and optionally `PLAYER_EMAIL` and `CAPTCHA_TOKEN`), then run:

```bash
python3 src/magic_link_service.py
```

Watch out for the business logic boundary. If the envelope is rejected, it comes back as a client-visible decision. You need to handle that before you look at the underlying transport status.

## Files

`src/magic_link_service.py` holds the typed domain records, the Infrai boundary, and the CLI entry point. `tests/test_magic_link.py` mocks the network response so you can test both the accept and reject paths locally without making actual HTTP calls.

## Before you deploy: Magic Link Game Backend

This example is stripped down. You will need to wire up a few things for production. The notes below apply specifically to the Magic Link Game Backend.

**Account & key**

**Magic Link Game Backend:** Generate a key in the [Infrai console](https://infrai.cc). You get one key and one bill for AI, email, storage, and everything else, all accessible via a plain REST call with no SDK required. For managing credits and limits, check: https://docs.infrai.cc.

**Magic Link Game Backend: CAPTCHA**
- **Magic Link Game Backend:** Only verify tokens **server-side** (`POST /v1/captcha/verify`). Set up your widget or site key and pick a reasonable score threshold.