import datetime

from django.core.management import call_command


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


def get_update_last_sync_date(sync_date: datetime.date):
    call_command('constance', 'set', 'LAST_SYNC_DATE', sync_date.strftime('%Y-%m-%d'))
