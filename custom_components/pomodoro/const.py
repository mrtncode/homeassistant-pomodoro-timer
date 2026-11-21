"""Constants for the Pomodoro integration."""

DOMAIN = "pomodoro"

CONF_FOCUS = "focus_minutes"
CONF_SHORT = "short_break_minutes"
CONF_LONG = "long_break_minutes"
CONF_CYCLES = "cycles_before_long_break"

DEFAULTS = {CONF_FOCUS: 25, CONF_SHORT: 5, CONF_LONG: 15, CONF_CYCLES: 4}

PHASE_IDLE = "idle"
PHASE_FOCUS = "focus"
PHASE_SHORT = "short_break"
PHASE_LONG = "long_break"
PHASES = [PHASE_IDLE, PHASE_FOCUS, PHASE_SHORT, PHASE_LONG]

PHASE_DURATION_KEY = {
    PHASE_FOCUS: CONF_FOCUS,
    PHASE_SHORT: CONF_SHORT,
    PHASE_LONG: CONF_LONG,
}

STATUS_IDLE = "idle"
STATUS_RUNNING = "running"
STATUS_PAUSED = "paused"

EVENT_PHASE_CHANGED = "pomodoro_phase_changed"
