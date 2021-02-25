from datetime import datetime
from logging import INFO, getLogger

from handler.clients import get_local_dt, send_time_teller_msg
from handler.jobs import Job

logger = getLogger("time_teller")
logger.setLevel(INFO)


def _is_same_hour_minute(dt_a: datetime, dt_b: datetime):
    return dt_a.hour == dt_b.hour and dt_a.minute == dt_b.minute


class _TimeTeller(Job):
    def __init__(self):
        self._last_tell_time = get_local_dt()

    def _should_trigger(self) -> bool:
        local_dt = get_local_dt()
        if _is_same_hour_minute(self._last_tell_time, local_dt):
            return False
        if local_dt.minute == 0 or local_dt.minute == 30:
            self._last_tell_time = local_dt
            return True

    def _action(self) -> None:
        send_time_teller_msg()
        logger.info("Sent time teller msg")
