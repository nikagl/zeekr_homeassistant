"""Adds config flow for Zeekr EV API Integration."""

import logging
import voluptuous as vol
from zeekr_ev_api.client import ZeekrClient

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    CONF_HMAC_ACCESS_KEY,
    CONF_HMAC_SECRET_KEY,
    CONF_PASSWORD,
    CONF_PASSWORD_PUBLIC_KEY,
    CONF_PROD_SECRET,
    CONF_USERNAME,
    CONF_VIN_IV,
    CONF_VIN_KEY,
    DOMAIN,
    PLATFORMS,
)

_LOGGER = logging.getLogger(__name__)


class ZeekrEVAPIFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for zeekr_ev_api_integration."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self) -> None:
        """Initialize."""
        self._errors = {}
        self._temp_client = None

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        if user_input is not None:
            valid = await self._test_credentials(
                user_input[CONF_USERNAME],
                user_input[CONF_PASSWORD],
                user_input[CONF_HMAC_ACCESS_KEY],
                user_input[CONF_HMAC_SECRET_KEY],
                user_input[CONF_PASSWORD_PUBLIC_KEY],
                user_input[CONF_PROD_SECRET],
                user_input[CONF_VIN_KEY],
                user_input[CONF_VIN_IV],
            )
            if valid:
                # Store the client for async_setup_entry to reuse
                self.hass.data.setdefault(DOMAIN, {})["_temp_client"] = (
                    self._temp_client
                )
                return self.async_create_entry(
                    title=user_input[CONF_USERNAME], data=user_input
                )
            self._errors["base"] = "auth"

            return await self._show_config_form(user_input)

        return await self._show_config_form(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return ZeekrEVAPIOptionsFlowHandler(config_entry)

    async def _show_config_form(self, user_input):
        """Show the configuration form to edit location data."""
        defaults = user_input or {}
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_USERNAME, default=defaults.get(CONF_USERNAME, "")
                    ): str,
                    vol.Required(
                        CONF_PASSWORD, default=defaults.get(CONF_PASSWORD, "")
                    ): str,
                    vol.Optional(
                        CONF_HMAC_ACCESS_KEY,
                        default=defaults.get(CONF_HMAC_ACCESS_KEY, ""),
                    ): str,
                    vol.Optional(
                        CONF_HMAC_SECRET_KEY,
                        default=defaults.get(CONF_HMAC_SECRET_KEY, ""),
                    ): str,
                    vol.Optional(
                        CONF_PASSWORD_PUBLIC_KEY,
                        default=defaults.get(CONF_PASSWORD_PUBLIC_KEY, ""),
                    ): str,
                    vol.Optional(
                        CONF_PROD_SECRET, default=defaults.get(CONF_PROD_SECRET, "")
                    ): str,
                    vol.Optional(
                        CONF_VIN_KEY, default=defaults.get(CONF_VIN_KEY, "")
                    ): str,
                    vol.Optional(
                        CONF_VIN_IV, default=defaults.get(CONF_VIN_IV, "")
                    ): str,
                }
            ),
            errors=self._errors,
        )

    async def _test_credentials(
        self,
        username,
        password,
        hmac_access_key,
        hmac_secret_key,
        password_public_key,
        prod_secret,
        vin_key,
        vin_iv,
    ):
        """Return true if credentials is valid."""
        try:
            client = ZeekrClient(
                username=username,
                password=password,
                hmac_access_key=hmac_access_key,
                hmac_secret_key=hmac_secret_key,
                password_public_key=password_public_key,
                prod_secret=prod_secret,
                vin_key=vin_key,
                vin_iv=vin_iv,
                logger=_LOGGER,
            )
            await self.hass.async_add_executor_job(client.login)
            self._temp_client = client
        except Exception:  # pylint: disable=broad-except
            pass
        else:
            return True
        return False


class ZeekrEVAPIOptionsFlowHandler(config_entries.OptionsFlow):
    """Config flow options handler for zeekr_ev_api_integration."""

    def __init__(self, config_entry):
        """Initialize HACS options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):  # pylint: disable=unused-argument
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self.options.update(user_input)
            return await self._update_options()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(x, default=self.options.get(x, True)): bool
                    for x in sorted(PLATFORMS)
                }
            ),
        )

    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(
            title=self.config_entry.data.get(CONF_USERNAME), data=self.options
        )
