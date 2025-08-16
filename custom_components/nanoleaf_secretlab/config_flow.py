import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from nanoleafapi import Nanoleaf

from .const import DOMAIN

class CannotConnect(HomeAssistantError):
    """Fehler beim Verbinden."""

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): str
})

async def validate_input(hass: HomeAssistant, data: dict):
    host = data[CONF_HOST]

    def get_token():
        nl = Nanoleaf(host)
        token = nl.generate_auth_token()  # Token erstellen
        return token

    try:
        token = await hass.async_add_executor_job(get_token)
    except Exception as err:
        raise CannotConnect from err

    return {"token": token}

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            else:
                self._host = user_input[CONF_HOST]
                self._token = info["token"]
                return await self.async_step_token_success()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors
        )

    async def async_step_token_success(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title="Nanoleaf Secretlab",
                data={"host": self._host, "token": self._token}
            )

        return self.async_show_form(
            step_id="token_success",
            description_placeholders={"token": self._token},
            data_schema=vol.Schema({})
        )
