import hashlib
import json
import logging
import datetime

from typing import Optional

from constance import config
from django.db import transaction

from apps.etl import schemas

from apps.core.models import (
    Area,
    Department,
    GP,
    Section,
    ResponsiblePerson,
    Project,
    StrategicTask,
    OperationalTask,
)
from apps.core.utils import calculate_status
from apps.etl.task_fetcher import TaskFetcher

INITIAL_DATA = json.loads(config.INITIAL_DATA_NAMES.replace("'", "\""))


class SyncTasks:

    def sync_all(
            self, sync_date: Optional[datetime.date]
    ):
        self.__sync_sections(sync_date)
        self.__sync_strategic_tasks(sync_date)
        self.__sync_operational_tasks(sync_date)

    @staticmethod
    def __sync_sections(sync_date):
        logging.info(f'Starting strategic tasks synchronization for {sync_date} date')
        fetcher = TaskFetcher()
        cursor = fetcher.get_cursor_for_sections(sync_date)
        while rows := cursor.fetchmany(1000):
            with transaction.atomic():
                for row in rows:
                    section = schemas.Section(
                        **dict((cursor.description[i][0], value) for i, value in enumerate(row))
                    )
                    Section.objects.get_or_create(name=section.name)
            logging.info(f'Successfully synchronization {len(rows)} sections')

        logging.info(f'Synchronization sections for {sync_date} completed')
        fetcher.close_cursor()

    @staticmethod
    def is_new_strategic_task(strategic_task: schemas.StrategicTask) -> bool:
        tasks = StrategicTask.objects.select_related(
            'gp', 'gp__project', 'section', 'responsible_person'
        ).filter(
            name=strategic_task.name,
            gp__name=strategic_task.gp,
            gp__project__name=strategic_task.project,
            gp__project__area__name=strategic_task.area,
            section__name=strategic_task.section or INITIAL_DATA['section_name'],
            start_date=strategic_task.start_date,
            finish_date=strategic_task.finish_date,
            baseline_start_date=strategic_task.baseline_start_date
            if strategic_task.baseline_start_date and strategic_task.baseline_finish_date
            else strategic_task.start_date,
            baseline_finish_date=strategic_task.baseline_finish_date
            if strategic_task.baseline_start_date and strategic_task.baseline_finish_date
            else strategic_task.finish_date,
            actual_finish_date=strategic_task.actual_finish_date,
            is_actual=strategic_task.is_actual,
            is_display=True if strategic_task.section else False,
            status=calculate_status(
                strategic_task.start_date,
                strategic_task.finish_date,
                strategic_task.baseline_start_date
                if strategic_task.baseline_start_date and strategic_task.baseline_finish_date
                else strategic_task.start_date,
                strategic_task.baseline_finish_date
                if strategic_task.baseline_start_date and strategic_task.baseline_finish_date
                else strategic_task.finish_date,
                strategic_task.actual_finish_date,
                strategic_task.is_actual,
            ),
            hash_code=strategic_task.hash_code
        )
        if strategic_task.responsible and strategic_task.email:
            tasks = tasks.filter(
                responsible_person__fullname=strategic_task.responsible,
                responsible_person__email=strategic_task.email
            )
        return not tasks.exists()

    def __sync_strategic_tasks(self, sync_date: Optional[datetime.date]):
        logging.info(f'Starting strategic tasks synchronization for {sync_date} date')
        fetcher = TaskFetcher()
        cursor = fetcher.get_cursor_for_strategic_tasks(sync_date)

        while rows := cursor.fetchmany(1000):
            with transaction.atomic():
                for row in rows:
                    strategic_task = schemas.StrategicTask(
                        **dict((cursor.description[i][0], value) for i, value in enumerate(row))
                    )
                    area, _ = Area.objects.get_or_create(name=strategic_task.area)
                    project, _ = Project.objects.get_or_create(name=strategic_task.project, area=area)
                    gp, _ = GP.objects.get_or_create(name=strategic_task.gp, project=project)
                    section, _ = Section.objects.get_or_create(name=strategic_task.section)
                    if strategic_task.responsible and strategic_task.email:
                        responsible_person, _ = ResponsiblePerson.objects.get_or_create(
                            fullname=strategic_task.responsible,
                            email=strategic_task.email
                        )
                    else:
                        responsible_person = None
                    if self.is_new_strategic_task(strategic_task):
                        StrategicTask.objects.create(
                            date=strategic_task.date,
                            name=strategic_task.name,
                            gp=gp,
                            start_date=strategic_task.start_date,
                            finish_date=strategic_task.finish_date,
                            baseline_start_date=strategic_task.baseline_start_date
                            if strategic_task.baseline_start_date and strategic_task.baseline_finish_date
                            else strategic_task.start_date,
                            baseline_finish_date=strategic_task.baseline_finish_date
                            if strategic_task.baseline_start_date and strategic_task.baseline_finish_date
                            else strategic_task.finish_date,
                            actual_finish_date=strategic_task.actual_finish_date,
                            is_actual=strategic_task.is_actual,
                            responsible_person=responsible_person,
                            section=section,
                            status=calculate_status(
                                strategic_task.start_date,
                                strategic_task.finish_date,
                                strategic_task.baseline_start_date
                                if strategic_task.baseline_start_date and strategic_task.baseline_finish_date
                                else strategic_task.start_date,
                                strategic_task.baseline_finish_date
                                if strategic_task.baseline_start_date and strategic_task.baseline_finish_date
                                else strategic_task.finish_date,
                                strategic_task.actual_finish_date,
                                strategic_task.is_actual,
                            ),
                            is_display=True if strategic_task.section else False,
                            hash_code=strategic_task.hash_code
                        )
            logging.info(f'Successfully synchronization {len(rows)} strategic tasks')
        logging.info(f'Synchronization strategic tasks for {sync_date} completed')
        fetcher.close_cursor()

    @staticmethod
    def is_new_operational_task(operational_task: schemas.OperationalTask) -> bool:
        tasks = OperationalTask.objects.select_related(
            'department', 'responsible_person'
        ).filter(
            name=operational_task.name,
            department__name=operational_task.department,
            start_date=operational_task.start_date,
            finish_date=operational_task.finish_date,
            baseline_start_date=operational_task.baseline_start_date
            if operational_task.baseline_start_date and operational_task.baseline_finish_date
            else operational_task.start_date,
            baseline_finish_date=operational_task.baseline_finish_date
            if operational_task.baseline_start_date and operational_task.baseline_finish_date
            else operational_task.finish_date,
            actual_finish_date=operational_task.actual_finish_date,
            is_actual=operational_task.is_actual,
            strategic_task=OperationalTask.get_strategic_task_for_hash_code(
                hash_code=operational_task.strat_hash_code, dt=operational_task.date
            ),
            status=calculate_status(
                operational_task.start_date,
                operational_task.finish_date,
                operational_task.baseline_start_date
                if operational_task.baseline_start_date and operational_task.baseline_finish_date
                else operational_task.start_date,
                operational_task.baseline_finish_date
                if operational_task.baseline_start_date and operational_task.baseline_finish_date
                else operational_task.finish_date,
                operational_task.actual_finish_date,
                operational_task.is_actual,
            ),
            hash_code=operational_task.hash_code
        )
        if operational_task.responsible and operational_task.email:
            tasks = tasks.filter(
                responsible_person__fullname=operational_task.responsible,
                responsible_person__email=operational_task.email
            )
        return not tasks.exists()

    def __sync_operational_tasks(self, sync_date: Optional[datetime.date]):
        logging.info(f'Starting operational tasks synchronization for {sync_date} date')
        fetcher = TaskFetcher()
        cursor = fetcher.get_cursor_for_operational_tasks(sync_date)

        while rows := cursor.fetchmany(1000):
            with transaction.atomic():
                for row in rows:
                    operational_task = schemas.OperationalTask(
                        **dict((cursor.description[i][0], value) for i, value in enumerate(row))
                    )
                    department, _ = Department.objects.get_or_create(name=operational_task.department)
                    if operational_task.responsible and operational_task.email:
                        responsible_person, _ = ResponsiblePerson.objects.get_or_create(
                            fullname=operational_task.responsible,
                            email=operational_task.email
                        )
                    else:
                        responsible_person = None
                    if self.is_new_operational_task(operational_task):
                        OperationalTask.objects.create(
                            date=operational_task.date,
                            name=operational_task.name,
                            start_date=operational_task.start_date,
                            finish_date=operational_task.finish_date,
                            baseline_start_date=operational_task.baseline_start_date
                            if operational_task.baseline_start_date and operational_task.baseline_finish_date
                            else operational_task.start_date,
                            baseline_finish_date=operational_task.baseline_finish_date
                            if operational_task.baseline_start_date and operational_task.baseline_finish_date
                            else operational_task.finish_date,
                            actual_finish_date=operational_task.actual_finish_date,
                            is_actual=operational_task.is_actual,
                            responsible_person=responsible_person,
                            department=department,
                            strategic_task=OperationalTask.get_strategic_task_for_hash_code(
                                hash_code=operational_task.strat_hash_code, dt=operational_task.date
                            ),
                            status=calculate_status(
                                operational_task.start_date,
                                operational_task.finish_date,
                                operational_task.baseline_start_date
                                if operational_task.baseline_start_date and operational_task.baseline_finish_date
                                else operational_task.start_date,
                                operational_task.baseline_finish_date
                                if operational_task.baseline_start_date and operational_task.baseline_finish_date
                                else operational_task.finish_date,
                                operational_task.actual_finish_date,
                                operational_task.is_actual,
                            ),
                            hash_code=operational_task.hash_code
                        )
            logging.info(f'Successfully synchronization {len(rows)} operational tasks')
        logging.info(f'Synchronization operational tasks for {sync_date} completed')
        fetcher.close_cursor()
