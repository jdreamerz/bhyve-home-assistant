from homeassistant import config_entries
from .const import DOMAIN


class BHyveConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle an options flow for BHyve."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize bhyve options flow."""
        self.config_entry = config_entry

    async def async_step_user(self, info):
        if info is not None:
            pass  # TODO: process info

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema({vol.Required("username"): str, vol.Required("password"): str,})
        )
