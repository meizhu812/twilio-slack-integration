from abc import ABC, abstractmethod
from logging import INFO, getLogger
from time import sleep

from handler.configs import RESTING_REPORT_INTERVAL, WORK_TIME_END, WORK_TIME_START
from handler.clients import get_local_dt, send_farewell_msg, send_greeting_msg
from handler.jobs import Job

REFRESH_INTERVAL = 5

logger = getLogger("job_handler")
logger.setLevel(INFO)


def _is_working_time() -> bool:
    return WORK_TIME_START <= get_local_dt().time() <= WORK_TIME_END


class _JobHandler:
    def __init__(self, *, jobs: list[Job]):
        self._jobs = jobs
        if _is_working_time():
            self._state = _WorkingState(self, init_state=True)
        else:
            self._state = _RestingState(self, init_state=True)

    def run(self):
        logger.info("Job handler running")
        while True:
            sleep(REFRESH_INTERVAL)
            self._state.refresh()

    def set_state(self, state: "_HandlerState"):
        self._state = state

    @property
    def jobs(self) -> list[Job]:
        return self._jobs


class _HandlerState(ABC):
    def __init__(self, _handler: _JobHandler, *, init_state: bool = False):
        self._handler = _handler
        if not init_state:
            self._on_set_state()

    def refresh(self):
        self._handle_jobs()
        if self._should_change_state():
            self._handler.set_state(self._next_state())

    @abstractmethod
    def _on_set_state(self):
        pass

    @abstractmethod
    def _handle_jobs(self):
        pass

    @staticmethod
    @abstractmethod
    def _should_change_state() -> bool:
        pass

    @abstractmethod
    def _next_state(self) -> "_HandlerState":
        pass


class _RestingState(_HandlerState):
    def __init__(self, _handler: _JobHandler, *, init_state: bool = False):
        super().__init__(_handler, init_state=init_state)
        local_dt = get_local_dt()
        self._start_time = local_dt
        self._last_report_time = local_dt

    def _on_set_state(self):
        logger.info("Resting...")
        send_farewell_msg()

    @staticmethod
    def _should_change_state() -> bool:
        return _is_working_time()

    def _next_state(self) -> _HandlerState:
        return _WorkingState(self._handler)

    def _handle_jobs(self):
        local_dt = get_local_dt()
        if (local_dt - self._last_report_time).seconds > RESTING_REPORT_INTERVAL:
            logger.info(f"Resting for {(local_dt - self._start_time).seconds} seconds")
            self._last_report_time = local_dt


class _WorkingState(_HandlerState):
    def _on_set_state(self):
        logger.info("Begin to work...")
        send_greeting_msg()

    def _handle_jobs(self):
        for job in self._handler.jobs:
            job.check()

    @staticmethod
    def _should_change_state() -> bool:
        return not _is_working_time()

    def _next_state(self) -> _HandlerState:
        return _RestingState(self._handler)
