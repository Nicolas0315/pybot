"""Stop the clock, so a reply that mentions the date or the time is the same on every run.

The bot reads the date through `datetime.date.today()` and `datetime.datetime.now()`, and answers
"what time is it" and a few lines about weekdays and months from them. `freeze()` swaps both in the
`datetime` module for subclasses that always report the same moment. Call it before the first reply.
"""
import datetime

MOMENT = datetime.datetime(2026, 11, 24, 15, 18, 0, tzinfo=datetime.timezone.utc)

_real_date = datetime.date
_real_datetime = datetime.datetime


class FrozenDate(_real_date):
    @classmethod
    def today(cls):
        return cls(MOMENT.year, MOMENT.month, MOMENT.day)


class FrozenDateTime(_real_datetime):
    @classmethod
    def now(cls, tz=None):
        moment = MOMENT if tz is None else MOMENT.astimezone(tz)
        return cls(moment.year, moment.month, moment.day, moment.hour, moment.minute, moment.second,
                   tzinfo=moment.tzinfo if tz is not None else None)

    @classmethod
    def utcnow(cls):
        return cls(MOMENT.year, MOMENT.month, MOMENT.day, MOMENT.hour, MOMENT.minute, MOMENT.second)

    @classmethod
    def today(cls):
        return cls.now()


def freeze():
    datetime.date = FrozenDate
    datetime.datetime = FrozenDateTime
