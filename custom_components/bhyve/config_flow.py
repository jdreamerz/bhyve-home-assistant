import voluptuous as vol

from homeassistant import config_entries

from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
)

from .const import DOMAIN

class BHyveConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle an options flow for BHyve."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize bhyve options flow."""

    @callback
    def _show_setup_form(self, user_input=None, errors=None):
        """Show the setup form to the user."""

        if user_input is None:
            user_input = {}

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_USERNAME, default=user_input.get(CONF_USERNAME, "")
                    ): str,
                    vol.Optional(CONF_PASSWORD): str,
                }
            ),
            errors=errors or {},
        )

    async def async_step_user(self, user_input):
        if self.hass.config_entries.async_entries(DOMAIN):
            return self.async_abort(reason="already_configured")

        if user_input is None:
            return self._show_setup_form(user_input)

        errors = {}
        username = user_input.get(CONF_USERNAME)
        password = user_input.get(CONF_PASSWORD)

        if not username:
            errors["base"] = "username"
        
        if not password:
            errors["base"] = "password"

        if errors:
            return self._show_setup_form(user_input, errors)

        return self.async_create_entry(
            title=self._host,
            data=user_input,
        )

    async def async_step_import(self, user_input=None):
        """Import a config entry."""
        return await self.async_step_user(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)
