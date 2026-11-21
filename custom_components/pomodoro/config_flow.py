"""Config + options flow."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_NAME
from homeassistant.core import callback

from .const import (
    CONF_CYCLES,
    CONF_FOCUS,
    CONF_LONG,
    CONF_SHORT,
    DEFAULTS,
    DOMAIN,
)


def _durations(current: dict[str, Any]) -> dict:
    minutes = vol.All(vol.Coerce(int), vol.Range(min=1, max=240))
    return {
        vol.Required(CONF_FOCUS, default=current[CONF_FOCUS]): minutes,
        vol.Required(CONF_SHORT, default=current[CONF_SHORT]): minutes,
        vol.Required(CONF_LONG, default=current[CONF_LONG]): minutes,
        vol.Required(CONF_CYCLES, default=current[CONF_CYCLES]): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=12)
        ),
    }


class PomodoroConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            data = dict(user_input)
            name = data.pop(CONF_NAME)
            return self.async_create_entry(title=name, data=data)
        schema = vol.Schema(
            {vol.Required(CONF_NAME, default="Pomodoro"): str, **_durations(DEFAULTS)}
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return PomodoroOptionsFlow()


class PomodoroOptionsFlow(OptionsFlow):
    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        current = {**DEFAULTS, **self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(
            step_id="init", data_schema=vol.Schema(_durations(current))
        )
