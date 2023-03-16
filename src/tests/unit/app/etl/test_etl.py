import pytest

from apps.etl.sync import SyncTasks


@pytest.mark.django_db
def test_sync_all(mock_operational_tasks, mock_strategic_tasks):
	SyncTasks(mock_operational_tasks, mock_strategic_tasks).sync_all()
