import logging
import os

from handler.configs import LOG_DATE_FORMAT, LOG_FORMAT, MAX_RETRIES
from handler import handler
from handler.clients import send_shutting_down_message

logger = logging.getLogger("main")
logger.setLevel(logging.INFO)

if __name__ == "__main__":
    logging.basicConfig(
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
    )
    logger.info("Starting up >>>>")
    logger.info(f"Current SLACK_ENV is {os.getenv('SLACK_ENV')}")
    _failed_times = 0
    while True:
        try:
            handler.run()
            _failed_times = 0
        except Exception as e:
            if (_failed_times := _failed_times + 1) > MAX_RETRIES:
                logger.error("Max retries exceeded")
                try:
                    send_shutting_down_message(failed_times=_failed_times)
                except Exception as e:
                    logger.warning(
                        f"Exception during sending shutting down message: {e}"
                    )
                break
            logger.warning(f"Exception: {e}")
            logger.warning(f"Service Restarting ({_failed_times}/{MAX_RETRIES})")
    logger.info("Shutting down >>>>")
