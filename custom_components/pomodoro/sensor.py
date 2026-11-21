"""Pomodoro sensors."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import PomodoroConfigEntry
from .const import PHASES
from .entity import PomodoroEntity


class _PomodoroSensor(PomodoroEntity, SensorEntity):
    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, self.timer.signal, self.async_write_ha_state
            )
        )


class PhaseSensor(_PomodoroSensor):
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = PHASES

    def __init__(self, timer) -> None:
        super().__init__(timer, "phase")

    @property
    def native_value(self) -> str:
        return self.timer.phase

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        paused = self.timer.paused_remaining
        return {
            "status": self.timer.status,  # idle / running / paused
            "cycles_done": self.timer.cycles_done,
            "paused_remaining_seconds": int(paused.total_seconds()) if paused else None,
        }


class EndSensor(_PomodoroSensor):
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, timer) -> None:
        super().__init__(timer, "end")

    @property
    def native_value(self) -> datetime | None:
        return self.timer.end


async def async_setup_entry(
    hass: HomeAssistant, entry: PomodoroConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    timer = entry.runtime_data
    async_add_entities([PhaseSensor(timer), EndSensor(timer)])
