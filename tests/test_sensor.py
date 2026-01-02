from zeekr_ev.sensor import ZeekrSensor


class DummyCoordinator:
    def __init__(self, data):
        self.data = data


def test_native_value_none_when_no_data():
    coordinator = DummyCoordinator({})
    s = ZeekrSensor(coordinator, "VIN1", "battery_level", "Battery", lambda d: 1, "%")
    assert s.native_value is None


def test_native_value_returns_value():
    data = {
        "VIN1": {
            "additionalVehicleStatus": {"electricVehicleStatus": {"chargeLevel": 42}}
        }
    }
    coordinator = DummyCoordinator(data)
    s = ZeekrSensor(
        coordinator,
        "VIN1",
        "battery_level",
        "Battery",
        lambda d: d.get("additionalVehicleStatus", {}).get("electricVehicleStatus", {}).get("chargeLevel"),
        "%",
    )
    assert s.native_value == 42


def test_charging_voltage_sensor():
    data = {
        "VIN1": {
            "chargingStatus": {"chargeVoltage": "222.0"}
        }
    }
    coordinator = DummyCoordinator(data)
    s = ZeekrSensor(
        coordinator,
        "VIN1",
        "charge_voltage",
        "Charge Voltage",
        lambda d: d.get("chargingStatus", {}).get("chargeVoltage"),
        "V",
    )
    assert s.native_value == "222.0"


def test_charging_current_sensor():
    data = {
        "VIN1": {
            "chargingStatus": {"chargeCurrent": "9.4"}
        }
    }
    coordinator = DummyCoordinator(data)
    s = ZeekrSensor(
        coordinator,
        "VIN1",
        "charge_current",
        "Charge Current",
        lambda d: d.get("chargingStatus", {}).get("chargeCurrent"),
        "A",
    )
    assert s.native_value == "9.4"


def test_charge_power_sensor():
    data = {
        "VIN1": {
            "chargingStatus": {"chargePower": "2.1"}
        }
    }
    coordinator = DummyCoordinator(data)
    s = ZeekrSensor(
        coordinator,
        "VIN1",
        "charge_power",
        "Charge Power",
        lambda d: d.get("chargingStatus", {}).get("chargePower"),
        "kW",
    )
    assert s.native_value == "2.1"


def test_charger_state_sensor():
    data = {
        "VIN1": {
            "chargingStatus": {"chargerState": "2"}
        }
    }
    coordinator = DummyCoordinator(data)
    s = ZeekrSensor(
        coordinator,
        "VIN1",
        "charger_state",
        "Charger State",
        lambda d: d.get("chargingStatus", {}).get("chargerState"),
    )
    assert s.native_value == "2"
