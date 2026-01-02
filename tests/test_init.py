from zeekr_ev import __init__ as comp_init


class DummyEntry:
    def __init__(self, data=None, entry_id="entry1"):
        self.data = data or {}
        self.entry_id = entry_id

    def async_on_unload(self, cb):
        pass


async def test_async_setup_entry_missing_credentials(hass):
    entry = DummyEntry(data={})
    res = await comp_init.async_setup_entry(hass, entry)
    assert res is False
