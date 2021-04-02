import os
from datetime import time, timedelta, timezone
from ssl import SSLContext

from slack_sdk import WebClient
from twilio.rest.api.v2010.account.message import MessageInstance

from handler.configs import (
    CHANNEL_ID,
    PATTERN,
    PHONE_NO_PREFIX,
    TIMESTAMP_FORMAT,
    WORK_TIME_END,
    WORK_TIME_START,
)
from credentials import ADMIN_ID, ALLOW_LIST, BOT_TOKEN
from handler.clients._ntp_client import get_local_dt

slack_bot = WebClient(token=BOT_TOKEN, ssl=SSLContext())
channel = CHANNEL_ID if os.getenv("SLACK_ENV") == "prod" else f"{CHANNEL_ID}_dev"
print(channel)


def _send_slack_message(msg: str):
    slack_bot.chat_postMessage(channel=channel, text=msg, link_names=True)


num_map = {
    "0": "zero",
    "1": "one",
    "2": "two",
    "3": "three",
    "4": "four",
    "5": "five",
    "6": "six",
    "7": "seven",
    "8": "eight",
    "9": "nine",
}


def _replace_num(message: str):
    for (digit, word) in num_map.items():
        message = message.replace(digit, f":{word}:")
    return message


def _get_emoji_time(_time: time):
    return _replace_num(_time.strftime("%H *:* %M"))


def _add_warning_affixes(s: str) -> str:
    return f":warning:{s}:warning:"


def send_greeting_msg():
    _send_slack_message(
        f"@here\n"
        f"Good morning devs, I'll be `working` "
        f"from  {_get_emoji_time(WORK_TIME_START)}  "
        f"to  {_get_emoji_time(WORK_TIME_END)}  today.\n"
        f"Have a nice day! :city_sunrise:"
    )


def send_farewell_msg():
    _send_slack_message(
        f"@here\n"
        f"Goodbye devs, I'll be `off-duty` "
        f"till  {_get_emoji_time(WORK_TIME_START)}  tomorrow.\n"
        f"Have a wonderful evening! :city_sunset:"
    )


def send_time_teller_msg():
    local_dt = get_local_dt()
    emoji_time = _get_emoji_time(local_dt.time())
    hour_without_padding = local_dt.strftime("%I").removeprefix("0")
    analog = (
        f"{hour_without_padding}30"
        if local_dt.minute == 30
        else f"{hour_without_padding}"
    )
    _send_slack_message(f"{emoji_time}    :clock{analog}:")


def publish_otp_from_msg(msg: MessageInstance):
    # noinspection PyUnresolvedReferences
    local_ts = msg.date_sent.astimezone(
        tz=timezone(offset=timedelta(hours=8))
    ).strftime(TIMESTAMP_FORMAT)
    phone_no = f"{msg.to.removeprefix(PHONE_NO_PREFIX)}"
    if phone_no not in ALLOW_LIST:
        phone_no = f"{_add_warning_affixes(f'`{phone_no}`')}"
    else:
        phone_no = f"`{phone_no}`"
    code = PATTERN.search(msg.body).group("code")
    _send_slack_message(
        f'\n`{local_ts}`  <{f"{phone_no}"}>    {f"{_replace_num(code)}"}'
    )


def send_shutting_down_message(*, failed_times: int):
    _send_slack_message(
        f"@here Service failed too many times ({failed_times}) and is shutting down, "
        f"please contact <@{ADMIN_ID}>"
    )
