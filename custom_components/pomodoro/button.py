"""Pomodoro buttons."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import PomodoroConfigEntry
from .entity import PomodoroEntity

BUTTONS = {"toggle": "toggle", "skip": "advance", "reset": "reset"}


class PomodoroButton(PomodoroEntity, ButtonEntity):
    def __init__(self, timer, key: str, method: str) -> None:
        super().__init__(timer, key)
        self._method = method

    async def async_press(self) -> None:
        getattr(self.timer, self._method)()


async def async_setup_entry(
    hass: HomeAssistant, entry: PomodoroConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    timer = entry.runtime_data
    async_add_entities(
        PomodoroButton(timer, key, method) for key, method in BUTTONS.items()
    )
