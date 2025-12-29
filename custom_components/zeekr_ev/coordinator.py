"""DataUpdateCoordinator for Zeekr EV API Integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from zeekr_ev_api.client import Vehicle, ZeekrClient

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class ZeekrCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Zeekr data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: ZeekrClient,
        entry: ConfigEntry,
    ) -> None:
        """Initialize."""
        self.client = client
        self.entry = entry
        self.vehicles: list[Vehicle] = []
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=5),
        )

    def get_vehicle_by_vin(self, vin: str) -> Vehicle | None:
        """Get a vehicle by VIN."""
        for vehicle in self.vehicles:
            if vehicle.vin == vin:
                return vehicle
        return None

    async def _async_update_data(self) -> dict[str, dict]:
        """Fetch data from API endpoint."""
        try:
            # Refresh vehicle list if empty (first run)
            if not self.vehicles:
                self.vehicles = await self.hass.async_add_executor_job(
                    self.client.get_vehicle_list
                )

            data = {}
            for vehicle in self.vehicles:
                # get_status returns a dict, no need to wrap if it was a property, but it's a method calling network
                vehicle_data = await self.hass.async_add_executor_job(
                    vehicle.get_status
                )
                data[vehicle.vin] = vehicle_data
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        else:
            return data
