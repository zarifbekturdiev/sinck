from datetime import date, timedelta
from typing import Optional

from constance import config

from apps.core.models import Statuses


def calculate_status(
        start_date: date,
        finish_date: date,
        baseline_start_date: Optional[date],
        baseline_finish_date: Optional[date],
        actual_finish_date: Optional[date],
        is_actual: bool,
):
    today = date.today()

    if not is_actual:
        return Statuses.NOT_ACTUAL
    if actual_finish_date:
        if (today - actual_finish_date).days <= config.CONTROL_PERIOD_IN_DAYS and finish_date > baseline_finish_date:
            return Statuses.OVERDUE_BY_DEADLINE
        else:
            return Statuses.COMPLETED_ON_TIME
    else:
        if today > baseline_finish_date or today > finish_date:
            return Statuses.OVERDUE
        elif finish_date > baseline_finish_date:
            return Statuses.OVERDUE_RISK
        elif start_date > today + timedelta(days=config.CONTROL_PERIOD_IN_DAYS) and \
                baseline_start_date > today + timedelta(days=config.CONTROL_PERIOD_IN_DAYS):
            return Statuses.FUTURE_TASK
        elif not (finish_date <= baseline_finish_date):
            return Statuses.OVERDUE_RISK
        elif min(
                today, baseline_start_date
        ) <= min(
            today + timedelta(days=config.CONTROL_PERIOD_IN_DAYS), baseline_finish_date
        ):
            return Statuses.IN_PROGRESS
        elif min(today, start_date) <= min(today + timedelta(days=config.CONTROL_PERIOD_IN_DAYS), finish_date):
            return Statuses.IN_PROGRESS
        elif today <= start_date <= today + timedelta(days=config.CONTROL_PERIOD_IN_DAYS) or \
                today <= baseline_start_date <= today + timedelta(days=config.CONTROL_PERIOD_IN_DAYS):
            return Statuses.IN_PROGRESS
    return Statuses.COMPLETED_ON_TIME
