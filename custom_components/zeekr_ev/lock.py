"""Lock platform for Zeekr EV API Integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.lock import LockEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ZeekrCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the lock platform."""
    coordinator: ZeekrCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[ZeekrLock] = []

    # Fields from drivingSafetyStatus to expose as lock-like entities
    lock_fields = {
        "centralLockingStatus": "Central locking",
        "doorLockStatusDriver": "Driver door lock",
        "doorLockStatusPassenger": "Passenger door lock",
        "doorLockStatusDriverRear": "Driver rear door lock",
        "doorLockStatusPassengerRear": "Passenger rear door lock",
        "trunkLockStatus": "Trunk lock",
        "engineHoodOpenStatus": "Hood (closed = locked)",
        "electricParkBrakeStatus": "Electric park brake",
        "tankFlapStatus": "Fuel flap (closed = locked)",
    }

    for vin in coordinator.data:
        for field, label in lock_fields.items():
            entities.append(ZeekrLock(coordinator, vin, field, label))

    async_add_entities(entities)


class ZeekrLock(CoordinatorEntity, LockEntity):
    """Zeekr Lock class representing various latch/lock states."""

    def __init__(
        self, coordinator: ZeekrCoordinator, vin: str, field: str, label: str
    ) -> None:
        """Initialize the lock entity for a specific field."""
        super().__init__(coordinator)
        self.vin = vin
        self.field = field
        self._attr_name = f"Zeekr {vin[-4:] if vin else ''} {label}"
        self._attr_unique_id = f"{vin}_{field}"

    @property
    def is_locked(self) -> bool | None:
        """Return true if lock is locked."""
        data = self.coordinator.data.get(self.vin, {})
        try:
            status = data.get("additionalVehicleStatus", {}).get(
                "drivingSafetyStatus", {}
            )

            val = status.get(self.field)
            # None means unknown
            if val is None:
                return None

            # Interpret values: many fields use "1" for active/locked, "0" for inactive/open
            # For *OpenStatus fields, treat "0" (closed) as locked True
            if self.field.endswith("OpenStatus"):
                return str(val) != "1"

            # For lock status fields and others, "1" -> locked
            return str(val) == "1"
        except (ValueError, TypeError, AttributeError):
            return None

    async def async_lock(self, **kwargs: Any) -> None:
        """Lock the car."""
        # Not implemented yet
        pass

    async def async_unlock(self, **kwargs: Any) -> None:
        """Unlock the car."""
        # Not implemented yet
        pass

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self.vin)},
            "name": f"Zeekr {self.vin}",
            "manufacturer": "Zeekr",
        }
