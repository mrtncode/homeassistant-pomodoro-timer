"""Pomodoro event entities."""

from __future__ import annotations

from typing import Any, ClassVar

from homeassistant.components.event import EventEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import PomodoroConfigEntry
from .const import PHASES
from .entity import PomodoroEntity


class PhaseChangedEvent(PomodoroEntity, EventEntity):
    _attr_event_types: ClassVar[list[str]] = ["phase_changed"]

    def __init__(self, timer) -> None:
        super().__init__(timer, "phase_changed")
        self._event_attributes: dict[str, Any] = {}
        self._last_phase: str | None = timer.phase

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return self._event_attributes

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(self.hass, self.timer.signal, self._timer_updated)
        )

    def _timer_updated(self) -> None:
        phase = self.timer.phase
        previous = self._last_phase
        self._last_phase = phase
        if previous is None or previous == phase or phase not in PHASES:
            return

        self._event_attributes = {
            "entry_id": self.timer.entry.entry_id,
            "name": self.timer.entry.title,
            "phase": phase,
            "previous_phase": previous,
        }
        self._trigger_event("phase_changed")


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PomodoroConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([PhaseChangedEvent(entry.runtime_data)])
