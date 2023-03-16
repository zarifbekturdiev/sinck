import pytest

from django.urls import reverse


from apps.core.models import Area, Project


@pytest.mark.django_db
@pytest.mark.parametrize(
	"view_basename",
	[
		'area-list',
		'project-list',
		'gp-list',
		'operational_task-list',
		'strategic_task-list',
		'section-list',
		'statuses',
	]
)
def test_api_response(client, view_basename):
	# проверяет работспособность api
	url = reverse(view_basename)
	response = client.get(url)
	assert response.status_code == 200
	

@pytest.fixture
def new_area():
	return Area.objects.create(name="Test Area")


@pytest.mark.django_db
def test_filter_project(client, new_area):
	# проверяет работоспособность фильтров
	url = reverse('project-list')
	Project.objects.create(name="Test Project", area=new_area)
	response = client.get(url, data={'area__id': new_area.pk})
	assert len(response.data) == 1
	
	