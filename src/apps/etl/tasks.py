from datetime import timedelta
from celery.utils.log import get_task_logger
from django.core.mail import send_mail
from django.conf import settings
from django.utils.timezone import now

from conf.celery import app as celery_app
from conf.utils import get_update_last_sync_date
from .sync import SyncTasks
from apps.core.models import OperationalTask, StrategicTask
from constance import config

logger = get_task_logger(__name__)


@celery_app.task(
    bind=True, name='etl.run_sync_tasks',
    retry_kwargs={'max_retries': config.SYNCHRONIZATION_RETRIES_COUNT - 1}
)
def run_sync_tasks(self):
    """
        Запуск синхронизации данных из бд
    """

    try:
        try:
            last_sync_date = config.LAST_SYNC_DATE
            last_operational_task = OperationalTask.objects.filter(date__isnull=False).order_by('-date').first()
            last_strategic_task = StrategicTask.objects.filter(date__isnull=False).order_by('-date').first()
            if last_strategic_task:
                last_sync_date = min(last_sync_date, last_strategic_task.date or last_sync_date)
            if last_operational_task:
                last_sync_date = min(last_sync_date, last_operational_task.date or last_sync_date)
            for i in range((now().date() - last_sync_date + timedelta(days=1)).days):
                SyncTasks().sync_all(sync_date=last_sync_date + timedelta(days=i))
            get_update_last_sync_date(now().date())
        except Exception as e:
            logger.error(f'Synchronization failed {str(e)}, retries {self.request.retries + 1}')
            raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))
        else:
            # Уведомления администратора о удачной синхронизации данных
            send_mail(
                'Cинхронизации данных',
                f'Синхронизация данных с {settings.DATABASES["source"]["NAME"]} успешно завершена.\n'
                f'Время: {now().strftime("%Y-%m-%d %H:%M:%S")}\n',
                settings.DEFAULT_FROM_EMAIL,
                [config.SUP_ADMIN_EMAIL],
                fail_silently=False
            )
            logger.info('Synchronization successfully completed')
    except Exception as exc:
        # Уведомления администратора о неудачной синхронизации данных
        send_mail(
            'Ошибка синхронизации данных',
            f'Неудачная попытка синхронизации данных с {settings.DATABASES["source"]["NAME"]}\n'
            f'Время: {now().strftime("%Y-%m-%d %H:%M:%S")}\n'
            f'Ошибка: {str(exc)}',
            settings.DEFAULT_FROM_EMAIL,
            [config.SUP_ADMIN_EMAIL],
            fail_silently=False
        )
