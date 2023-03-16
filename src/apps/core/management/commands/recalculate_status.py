from apps.core.utils import calculate_status
from apps.core.models import OperationalTask, StrategicTask

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Recalculate tasks statuses'

    def handle(self, *args, **options):
        operational_tasks = OperationalTask.objects.all()
        for operational_task in operational_tasks:
            operational_task.status = calculate_status(
                operational_task.start_date,
                operational_task.finish_date,
                operational_task.baseline_start_date,
                operational_task.baseline_finish_date,
                operational_task.actual_finish_date,
                operational_task.is_actual
            )
        OperationalTask.objects.bulk_update(objs=operational_tasks, batch_size=1000, fields=['status'])
        self.stdout.write(
            self.style.SUCCESS('Successfully recalculate status operational tasks "%s"' % operational_tasks.count())
        )
        strategic_tasks = StrategicTask.objects.all()
        for strategic_task in strategic_tasks:
            strategic_task.status = calculate_status(
                strategic_task.start_date,
                strategic_task.finish_date,
                strategic_task.baseline_start_date,
                strategic_task.baseline_finish_date,
                strategic_task.actual_finish_date,
                strategic_task.is_actual
            )
        StrategicTask.objects.bulk_update(objs=strategic_tasks, batch_size=1000, fields=['status'])
        self.stdout.write(
            self.style.SUCCESS('Successfully recalculate status strategic tasks "%s"' % strategic_tasks.count())
        )
