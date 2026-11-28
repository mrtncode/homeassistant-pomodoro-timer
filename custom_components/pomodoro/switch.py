"""Pomodoro timer switch."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import PomodoroConfigEntry
from .const import STATUS_RUNNING
from .entity import PomodoroEntity


class PomodoroSwitch(PomodoroEntity, SwitchEntity):
    """Control whether the Pomodoro timer is running."""

    def __init__(self, timer) -> None:
        super().__init__(timer, "timer")

    @property
    def is_on(self) -> bool:
        return self.timer.status == STATUS_RUNNING

    async def async_turn_on(self, **kwargs) -> None:
        if not self.is_on:
            self.timer.toggle()

    async def async_turn_off(self, **kwargs) -> None:
        if self.is_on:
            self.timer.toggle()

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, self.timer.signal, self.async_write_ha_state
            )
        )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PomodoroConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([PomodoroSwitch(entry.runtime_data)])
