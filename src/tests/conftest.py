import json

import pytest
from django.conf import settings
from django.core.management import call_command

from apps.etl import schemas


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', settings.BASE_DIR / 'tests' / 'fixture.json')


@pytest.fixture
def project_path():
    return settings.BASE_DIR / 'tests'


@pytest.fixture
def operational_task_file_path(project_path):
    return project_path / 'operational_tasks.json'


@pytest.fixture
def mock_operational_tasks(operational_task_file_path):
    with open(operational_task_file_path, encoding="utf8") as file:
        return schemas.OperationalTaskList(operational_tasks=json.load(file)).operational_tasks


@pytest.fixture
def strategic_task_file_path(project_path):
    return project_path / 'strategic_tasks.json'


@pytest.fixture
def mock_strategic_tasks(strategic_task_file_path):
    with open(strategic_task_file_path, encoding="utf8") as file:
        return schemas.StrategicTaskList(strategic_tasks=json.load(file)).strategic_tasks
