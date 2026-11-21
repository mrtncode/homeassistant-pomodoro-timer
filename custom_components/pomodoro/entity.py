"""Shared base entity."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import DOMAIN
from .timer import PomodoroTimer


class PomodoroEntity(Entity):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, timer: PomodoroTimer, key: str) -> None:
        self.timer = timer
        self._attr_translation_key = key
        self._attr_unique_id = f"{timer.entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, timer.entry.entry_id)}, name=timer.entry.title
        )
