from datetime import timedelta, timezone

from twilio.rest import Client

from credentials import T_PASSWORD, T_USERNAME
from handler.clients import get_local_dt

client = Client(T_USERNAME, T_PASSWORD)


def get_latest_msgs(*, within_seconds: int):
    utc_dt = get_local_dt().astimezone(timezone.utc)
    msgs = client.messages.list(limit=10)
    return list(
        filter(
            lambda msg: utc_dt - msg.date_sent < timedelta(seconds=within_seconds), msgs
        )
    )
