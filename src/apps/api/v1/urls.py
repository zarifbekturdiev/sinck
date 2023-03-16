from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.api.v1.views import *

router = DefaultRouter()

router.register(r'projects', ProjectView, basename='project')
router.register(r'areas', AreaView, basename='area')
router.register(r'gps', GPView, basename='gp')
router.register(r'sections', SectionView, basename='section')
router.register(r'departments', DepartmentView, basename='department')
router.register(r'operational_tasks', OperationalTaskView, basename='operational_task')
router.register(r'responsible_persons', ResponsiblePersonView, basename='responsible_person')

urlpatterns = [
    path('statuses', StatusesView.as_view(), name='statuses'),
    path('strategic_tasks', StrategicTaskAPIView.as_view(), name='strategic_tasks'),
]

urlpatterns += router.urls
