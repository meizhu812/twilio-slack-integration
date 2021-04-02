import re
from collections import deque

from yaml import safe_load
from datetime import time


def convert_to_time(hhmm: str):
    hh = hhmm[0:2]
    mm = hhmm[2:4]
    return time(int(hh), int(mm))


with open("./config.yaml") as config_file:
    config = safe_load(config_file)
# System


network_ = config["Network"]
MAX_RETRIES = network_["Max Retries"]
RESTING_REPORT_INTERVAL = network_["Resting Report Interval"]
NTP_DOMAINS = deque([f"{n}{network_['NTP Root Domain']}" for n in range(4)])

# Log
log_ = config["Log"]
LOG_FORMAT = log_["Log Format"]
LOG_DATE_FORMAT = log_["Timestamp Format"]

# SMS

sms_ = config["SMS"]
PHONE_NO_PREFIX = sms_["Region Number"]
PATTERN = re.compile(sms_["Message Pattern"])
TIMESTAMP_FORMAT = sms_["Timestamp Format"]

# Slack
slack_ = config["Slack"]
CHANNEL_ID = slack_["Channel Id"]
WORK_TIME_START = convert_to_time(slack_["Work Time"]["Start"])
WORK_TIME_END = convert_to_time(slack_["Work Time"]["End"])
