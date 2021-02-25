from abc import ABC, abstractmethod


class Job(ABC):
    def check(self):
        if self._should_trigger():
            self._action()

    @abstractmethod
    def _should_trigger(self) -> bool:
        pass

    @abstractmethod
    def _action(self) -> None:
        pass
