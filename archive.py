# class ArchiveTasks:
#     def run(self):
#         self.archive_operational_tasks()
#         # TODO продумать логику архивации стратгических задач.
#
#     @staticmethod
#     def archive_operational_tasks():
#         logging.info(f'Starting archive operational tasks')
#         operational_tasks = OperationalTask.objects.exclude(
#             Q(
#                 finish_date__gte=datetime.date.today() - datetime.timedelta(days=7),
#                 start_date__lte=datetime.date.today()
#             ) |
#             Q(
#                 baseline_finish_date__gte=datetime.date.today() - datetime.timedelta(days=7),
#                 baseline_start_date__lte=datetime.date.today()
#             )
#         )
#         for operational_task in operational_tasks:
#             ArchivedOperationalTask.objects.create(
#                 source_id=operational_task.source_id,
#                 date=operational_task.date,
#                 name=operational_task.name,
#                 start_date=operational_task.start_date,
#                 finish_date=operational_task.finish_date,
#                 baseline_start_date=operational_task.baseline_start_date,
#                 baseline_finish_date=operational_task.baseline_finish_date,
#                 actual_finish_date=operational_task.actual_finish_date,
#                 is_actual=operational_task.is_actual,
#                 responsible_person=operational_task.responsible_person,
#                 department=operational_task.department,
#                 strategic_task=ArchivedOperationalTask.get_archived_strategic_task(
#                     name=operational_task.strategic_task.name,
#                     gp=operational_task.strategic_task.gp
#                 ),
#                 status=calculate_status(
#                     operational_task.start_date,
#                     operational_task.finish_date,
#                     operational_task.baseline_start_date,
#                     operational_task.baseline_finish_date,
#                     operational_task.actual_finish_date,
#                     operational_task.is_actual,
#                 )
#             )
#         logging.info(f'Archived {operational_tasks.count()} operational tasks')
#         operational_tasks.delete()


import json

from django.db import migrations, models
from datetime import date

from constance import config
from django.contrib.auth.models import User
from django.db import migrations, models
import django.db.models.deletion

from apps.core.utils import calculate_status

INITIAL_DATA = json.loads(config.INITIAL_DATA_NAMES.replace("'", "\""))


def create_superuser(apps, schema_editor):
    superuser = User()
    superuser.is_active = True
    superuser.is_superuser = True
    superuser.is_staff = True
    superuser.username = 'admin'
    superuser.email = 'admin@example.com'
    superuser.set_password('adminpass_000')
    superuser.save()


def delete_superuser(apps, schema_editor):
    User.objects.first().delete()


def create_initial_strategic_task(apps, schema_editor):
    Area = apps.get_model('core', 'Area')
    Project = apps.get_model('core', 'Project')
    GP = apps.get_model('core', 'GP')
    StrategicTask = apps.get_model('core', 'StrategicTask')
    ArchivedStrategicTask = apps.get_model('core', 'ArchivedStrategicTask')
    Section = apps.get_model('core', 'Section')
    db_alias = schema_editor.connection.alias
    area = Area.objects.using(db_alias).create(name=INITIAL_DATA['area_name'])
    project = Project.objects.using(db_alias).create(name=INITIAL_DATA['project_name'], area_id=area.id)
    gp = GP.objects.using(db_alias).create(name=INITIAL_DATA['gp_name'], project_id=project.id)
    section = Section.objects.using(db_alias).create(name=INITIAL_DATA['section_name'])
    StrategicTask.objects.using(db_alias).create(
        name=INITIAL_DATA['strategic_task_name'],
        gp_id=gp.id,
        start_date=date(2000, 1, 1),
        finish_date=date(2030, 1, 1),
        baseline_start_date=date(2000, 1, 1),
        baseline_finish_date=date(2030, 1, 1),
        is_actual=True,
        status=calculate_status(
            date(2000, 1, 1), date(2030, 1, 1),
            date(2000, 1, 1), date(2030, 1, 1),
            None, True
        ),
        is_display=True,
        section_id=section.id,
        source_id=0,
    )
    ArchivedStrategicTask.objects.using(db_alias).create(
        name=INITIAL_DATA['archived_strategic_task_name'],
        gp_id=gp.id,
        start_date=date(2000, 1, 1),
        finish_date=date(2030, 1, 1),
        baseline_start_date=date(2000, 1, 1),
        baseline_finish_date=date(2030, 1, 1),
        is_actual=True,
        status=calculate_status(
            date(2000, 1, 1), date(2030, 1, 1),
            date(2000, 1, 1), date(2030, 1, 1),
            None, True
        ),
        is_display=True,
        section_id=section.id,
        source_id=0,
    )


def delete_initial_strategic_task(apps, schema_editor):
    Area = apps.get_model('core', 'Area')
    Section = apps.get_model('core', 'Section')
    db_alias = schema_editor.connection.alias
    # Достаточно удалить Регион так как установлен models.CASCADE
    Area.objects.using(db_alias).filter(name=INITIAL_DATA['area_name']).delete()
    Section.objects.using(db_alias).filter(name=INITIAL_DATA['section_name']).delete()


migrations.RunPython(create_superuser, delete_superuser),
migrations.RunPython(create_initial_strategic_task, delete_initial_strategic_task)
