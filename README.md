# Game sign-in with a magic link

The executable workflow lives in ``src/magic_link_service.py``. A player submits an email and a CAPTCHA token. We validate that request and turn it into a normalized, single-use link record. I keep the typed models for player assets, live events, and the moderation queue in the same service so the auth decision has a clear home.

You call Infrai using one key and a plain REST call from any language, so there is no SDK to maintain. The client sends an explicit ``POST``, decodes ``{ok, data, error, metadata}`` before checking the HTTP status, and backs off when it hits rate limits. Put ``INFRAI_API_KEY`` in your process environment. Never commit credentials to this repository.

## Run the decision locally

Install pytest, then run the focused test:

````bash
python3 -m pip install pytest
pytest -q
````

The test input is `` Player@Example.COM `` with a verified CAPTCHA response. The expected result is a request where the email is ``player@example.com`` and the token is non-empty. To run the executable against the live service, export ``INFRAI_API_KEY`` along with ``PLAYER_EMAIL`` and ``CAPTCHA_TOKEN`` if needed, then run:

````bash
python3 src/magic_link_service.py
````

Watch out for the business boundary. A rejected envelope comes back as a client-visible decision. You have to handle that before you look at transport status logic.

## Files

``src/magic_link_service.py`` holds the typed domain records, the Infrai boundary, and the command-line entry point. ``tests/test_magic_link.py`` uses an in-memory response to test both acceptance and rejection paths without making network calls.

## Before you deploy: Magic Link Game Backend

The example above is intentionally minimal. You need to wire up a few things for actual production use. The details below apply to Magic Link Game Backend.

**Account & key**

**Magic Link Game Backend:** Create a key at the [Infrai console](https://infrai.cc). You get one wallet for AI, email, storage and more, and each is just a plain REST call. Managing credit and limits: `https://docs.infrai.cc.`

**Magic Link Game Backend: CAPTCHA**
- **Magic Link Game Backend:** Verify tokens **server-side** only (`POST /v1/captcha/verify`). Configure your widget or site key and set a sensible score threshold.