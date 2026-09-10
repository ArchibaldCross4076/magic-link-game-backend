import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from magic_link_service import GameAuthService, InfraiClient, InfraiError


class FakeResponse:
    status = 200
    headers = {}

    def read(self):
        return json.dumps({"ok": True, "data": {"verified": True}, "error": None, "metadata": {}}).encode()


def test_verified_player_gets_normalized_magic_link_request():
    client = InfraiClient(api_key="test-key", opener=lambda request, timeout: FakeResponse())
    request = GameAuthService(client).request_magic_link(" Player@Example.COM ", "captcha-ok")
    assert request.email == "player@example.com"
    assert request.token


def test_rejected_envelope_is_business_error():
    class Rejected(FakeResponse):
        def read(self):
            return json.dumps({"ok": False, "data": None, "error": {"code": "CAPTCHA_SCORE_TOO_LOW"}, "metadata": {}}).encode()

    client = InfraiClient(api_key="test-key", opener=lambda request, timeout: Rejected())
    try:
        GameAuthService(client).request_magic_link("player@example.com", "bad")
    except InfraiError as error:
        assert error.code == "CAPTCHA_SCORE_TOO_LOW"
    else:
        raise AssertionError("rejection must stop link creation")
