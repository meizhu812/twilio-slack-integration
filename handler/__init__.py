from handler._handler import _JobHandler
from handler.jobs import otp_publisher, time_teller

handler = _JobHandler(jobs=[time_teller, otp_publisher])

__all__ = ["handler"]
