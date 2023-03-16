import pytest

from apps.core.models import (
    Area,
    Department,
    Project,
    GP,
)


@pytest.mark.django_db
def test_fixture(client):
    assert Area.objects.count() == 5
    assert Department.objects.count() == 5
    assert Project.objects.count() == 19
    assert GP.objects.count() == 60
