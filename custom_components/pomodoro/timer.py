"""Pomodoro state machine."""

from __future__ import annotations

from datetime import datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_call_later
from homeassistant.util import dt as dt_util

from .const import (
    CONF_CYCLES,
    DEFAULTS,
    DOMAIN,
    EVENT_PHASE_CHANGED,
    PHASE_DURATION_KEY,
    PHASE_FOCUS,
    PHASE_IDLE,
    PHASE_LONG,
    PHASE_SHORT,
    STATUS_IDLE,
    STATUS_PAUSED,
    STATUS_RUNNING,
)


class PomodoroTimer:
    """Focus -> short break -> ... -> long break, with pause/resume/skip/reset."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.phase = PHASE_IDLE
        self.status = STATUS_IDLE
        self.end: datetime | None = None
        self.paused_remaining: timedelta | None = None
        self.cycles_done = 0
        self._unsub: CALLBACK_TYPE | None = None

    @property
    def signal(self) -> str:
        return f"{DOMAIN}_update_{self.entry.entry_id}"

    def _cfg(self, key: str) -> int:
        return {**DEFAULTS, **self.entry.data, **self.entry.options}[key]

    def _cancel(self) -> None:
        if self._unsub:
            self._unsub()
            self._unsub = None

    def _schedule(self, delay: timedelta) -> None:
        self._cancel()
        self.end = dt_util.utcnow() + delay
        self._unsub = async_call_later(self.hass, delay, self._finished)

    def _notify(self, previous: str | None = None) -> None:
        async_dispatcher_send(self.hass, self.signal)
        if previous is not None and previous != self.phase:
            self.hass.bus.async_fire(
                EVENT_PHASE_CHANGED,
                {
                    "entry_id": self.entry.entry_id,
                    "name": self.entry.title,
                    "phase": self.phase,
                    "previous_phase": previous,
                },
            )

    @callback
    def _finished(self, _now: datetime) -> None:
        self._unsub = None
        self.advance()

    @callback
    def _start_phase(self, phase: str) -> None:
        previous = self.phase
        self.phase = phase
        self.status = STATUS_RUNNING
        self.paused_remaining = None
        self._schedule(timedelta(minutes=self._cfg(PHASE_DURATION_KEY[phase])))
        self._notify(previous)

    @callback
    def advance(self) -> None:
        """Jump to the next phase (also used when a phase runs out)."""
        if self.phase == PHASE_FOCUS:
            self.cycles_done += 1
            if self.cycles_done >= self._cfg(CONF_CYCLES):
                self.cycles_done = 0
                self._start_phase(PHASE_LONG)
            else:
                self._start_phase(PHASE_SHORT)
        else:
            self._start_phase(PHASE_FOCUS)

    @callback
    def toggle(self) -> None:
        """Start when idle, pause when running, resume when paused."""
        if self.status == STATUS_IDLE:
            self._start_phase(PHASE_FOCUS)
        elif self.status == STATUS_RUNNING:
            assert self.end is not None
            self.paused_remaining = max(self.end - dt_util.utcnow(), timedelta(0))
            self._cancel()
            self.end = None
            self.status = STATUS_PAUSED
            self._notify()
        else:
            remaining = self.paused_remaining or timedelta(0)
            self.paused_remaining = None
            self.status = STATUS_RUNNING
            self._schedule(remaining)
            self._notify()

    @callback
    def reset(self) -> None:
        previous = self.phase
        self._cancel()
        self.phase = PHASE_IDLE
        self.status = STATUS_IDLE
        self.end = None
        self.paused_remaining = None
        self.cycles_done = 0
        self._notify(previous)

    @callback
    def async_shutdown(self) -> None:
        self._cancel()
