"""Shared entity implementations for Zeekr EV API Integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ZeekrCoordinator


class ZeekrEntity(CoordinatorEntity[ZeekrCoordinator]):
    """Base entity for Zeekr."""

    def __init__(self, coordinator: ZeekrCoordinator, vin: str) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self.vin = vin
        vehicle = coordinator.get_vehicle_by_vin(vin)
        if vehicle:
            self._attr_device_info = DeviceInfo(
                identifiers={(DOMAIN, vin)},
                name=vehicle.vin,
                manufacturer="Zeekr",
                model=getattr(vehicle, "model", "Unknown"),
            )
