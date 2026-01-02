from custom_components.zeekr_ev.binary_sensor import ZeekrBinarySensor


class DummyCoordinator:
    def __init__(self, data):
        self.data = data


def test_is_on_none_when_no_data():
    coordinator = DummyCoordinator({})
    bs = ZeekrBinarySensor(coordinator, "VIN1", "charging_status", "Charging Status", lambda d: True)
    assert bs.is_on is None


def test_charging_status_true_false():
    data_true = {
        "VIN1": {"additionalVehicleStatus": {"electricVehicleStatus": {"isCharging": True}}}
    }
    coordinator = DummyCoordinator(data_true)
    bs = ZeekrBinarySensor(coordinator, "VIN1", "charging_status", "Charging Status", lambda d: d.get("additionalVehicleStatus", {}).get("electricVehicleStatus", {}).get("isCharging"))
    assert bs.is_on is True

    data_false = {
        "VIN1": {"additionalVehicleStatus": {"electricVehicleStatus": {"isCharging": False}}}
    }
    coordinator = DummyCoordinator(data_false)
    bs = ZeekrBinarySensor(coordinator, "VIN1", "charging_status", "Charging Status", lambda d: d.get("additionalVehicleStatus", {}).get("electricVehicleStatus", {}).get("isCharging"))
    assert bs.is_on is False
