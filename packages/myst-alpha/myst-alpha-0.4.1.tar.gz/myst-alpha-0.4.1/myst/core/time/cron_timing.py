from typing import Optional


class CronTiming:
    """A timing that specifies a schedule according to a cron string."""

    def __init__(self, cron_expression: str, time_zone: Optional[str] = "UTC"):
        """A `CronTiming` timing is initialized with a cron expression and an optional time delta.

        Args:
            cron_expression: a cron expression made of five fields representing minute, hour, day of month, month, and
                day of week
            time_zone: the time zone to schedule the cron with; defaults to UTC
        """
        self._cron_expression = cron_expression
        self._time_zone = time_zone
