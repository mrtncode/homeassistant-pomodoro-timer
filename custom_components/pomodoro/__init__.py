"""Pomodoro timer integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .timer import PomodoroTimer

PLATFORMS = [Platform.SENSOR, Platform.SWITCH, Platform.BUTTON, Platform.EVENT]

type PomodoroConfigEntry = ConfigEntry[PomodoroTimer]


async def async_setup_entry(hass: HomeAssistant, entry: PomodoroConfigEntry) -> bool:
    entry.runtime_data = PomodoroTimer(hass, entry)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: PomodoroConfigEntry) -> bool:
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        entry.runtime_data.async_shutdown()
    return ok
