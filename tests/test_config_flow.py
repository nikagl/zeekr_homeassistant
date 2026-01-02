import custom_components.zeekr_ev.config_flow as config_flow


class FakeClient:
    def __init__(self, succeed=True):
        self.succeed = succeed

    def login(self):
        if not self.succeed:
            raise Exception("bad creds")


async def test_test_credentials_success(hass, monkeypatch):
    # Replace ZeekrClient with FakeClient that succeeds
    monkeypatch.setattr(config_flow, "ZeekrClient", FakeClient)
    flow = config_flow.ZeekrEVAPIFlowHandler()
    flow.hass = hass
    ok = await flow._test_credentials(
        "user",
        "pass",
        "hmac_access",
        "hmac_secret",
        "pwd_pub",
        "prod_secret",
        "vin_key",
        "vin_iv",
    )
    assert ok is True
    assert flow._temp_client is not None


async def test_test_credentials_failure(hass, monkeypatch):
    # Replace ZeekrClient with FakeClient that raises on login
    monkeypatch.setattr(config_flow, "ZeekrClient", lambda **kwargs: FakeClient(succeed=False))
    flow = config_flow.ZeekrEVAPIFlowHandler()
    flow.hass = hass
    ok = await flow._test_credentials(
        "user",
        "bad",
        "hmac_access",
        "hmac_secret",
        "pwd_pub",
        "prod_secret",
        "vin_key",
        "vin_iv",
    )
    assert ok is False
