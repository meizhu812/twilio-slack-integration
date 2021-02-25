from logging import INFO, getLogger

from handler.clients import get_latest_msgs, publish_otp_from_msg
from handler.jobs._job import Job

logger = getLogger("otp_publisher")
logger.setLevel(INFO)


class _OTPPublisher(Job):
    def __init__(self):
        self._msg_sids = set()
        self._msgs = []

    def _should_trigger(self) -> bool:
        msgs = get_latest_msgs(within_seconds=20)
        for msg in msgs:
            if msg.sid not in self._msg_sids:
                self._msgs.append(msg)
        return len(self._msgs) > 0

    def _action(self) -> None:
        while len(self._msgs) > 0:
            msg = self._msgs.pop()
            self._msg_sids.add(msg.sid)
            try:
                logger.info(f"OTP sent to {msg.to}")
                publish_otp_from_msg(msg)
            except Exception as e:
                logger.error(f"Got an error: {e}")
