import os
from datetime import datetime, timedelta, timezone
from logging import INFO, getLogger

from ntplib import NTPClient

from handler.configs import MAX_RETRIES, NTP_DOMAINS

ntp_client = NTPClient()

logger = getLogger("time_util")
logger.setLevel(INFO)


def get_local_dt() -> datetime:
    if os.getenv("SLACK_ENV") != "prod":
        return _get_system_local_dt()
    try:
        return _get_ntp_local_dt()
    except Exception as e:
        logger.warning(e)
        return _get_system_local_dt()


def _get_ntp_local_dt():
    failed_times = 0
    while True:
        domain = NTP_DOMAINS[0]
        NTP_DOMAINS.rotate()
        if failed_times > MAX_RETRIES:
            raise RuntimeError("Reached MAX_RETRIES when getting ntp time")
        # noinspection PyBroadException
        try:
            ntp_stats = ntp_client.request(domain)
            failed_times = 0
            return datetime.fromtimestamp(
                ntp_stats.tx_time, tz=timezone.utc
            ).astimezone(tz=timezone(offset=timedelta(hours=8)))
        except Exception:
            failed_times += 1


def _get_system_local_dt():
    return datetime.now(tz=timezone(offset=timedelta(hours=8)))
