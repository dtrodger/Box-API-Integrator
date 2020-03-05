from __future__ import annotations
from typing import AnyStr, Optional, List
import logging.config

import slack
import twilio


DEFAULT_LOG_FORMAT = "[%(levelname)s] [%(asctime)s] [%(name)s] - %(message)s"


class SlackLogHandler(logging.Handler):
    log_level_emojis = {
        logging.NOTSET: ":loudspeaker:",
        logging.DEBUG: ":speaker:",
        logging.INFO: ":information_source:",
        logging.WARNING: ":warning:",
        logging.ERROR: ":exclamation:",
        logging.CRITICAL: ":boom:",
    }

    def __init__(
        self,
        access_key: AnyStr,
        channel: AnyStr,
        formatter: Optional[
            AnyStr
        ] = DEFAULT_LOG_FORMAT,
        level: Optional[int] = logging.NOTSET,
    ) -> SlackLogHandler:

        super().__init__(level=level)

        self.formatter = logging.Formatter(formatter)

        self._slack = slack.WebClient(access_key)
        self._channel = channel

    def emit(self, record: logging.LogRecord) -> None:
        try:
            emote = getattr(record, "slack_icon", self.log_level_emojis[record.levelno])
            log = self.format(record)
            content = f"{emote} {log}"
            self._slack.chat_postMessage(channel=self._channel, text=content)
        except Exception as e:
            self.handleError(record)


class SMSLogHandler(logging.Handler):
    def __init__(
        self,
        account_sid: AnyStr,
        auth_token: AnyStr,
        sender: AnyStr,
        recipients: List,
        formatter: Optional[
            AnyStr
        ] = DEFAULT_LOG_FORMAT,
    ) -> SMSLogHandler:

        super().__init__()

        self.formatter = logging.Formatter(formatter)

        self._twilio = twilio.rest.Client(account_sid, auth_token)
        self.sender = sender
        self.recipients = recipients

    def emit(self, record: logging.LogRecord) -> None:

        log = self.format(record)

        for number in self.recipients:
            try:
                self.twilio.messages.create(body=log, to=number, from_=self.sender)
            except Exception as e:
                self.handleError(record)
