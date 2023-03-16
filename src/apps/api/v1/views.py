from django.core.exceptions import BadRequest
from django.db.models import Prefetch, Q, Subquery
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.api.v1.serializers import *
from apps.core.models import Statuses


class AreaView(ReadOnlyModelViewSet):
    """Получение Регионов"""
    serializer_class = AreaSerializer
    queryset = Area.objects.distinct("name")


class ProjectView(ReadOnlyModelViewSet):
    """
    Получение проектов
    
    Parametrs
    ---------
    area__id : Фильтр по id региона
    """
    serializer_class = ProjectWithoutAreaSerializer
    queryset = Project.objects.distinct("name")
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('area__id',)


class GPView(ReadOnlyModelViewSet):
    """
    Получение ГП

    Parametrs
    ---------
    project__id : Фильтр по id проекта
    """
    serializer_class = GPWithoutProjectSerializer
    queryset = GP.objects.distinct("name")
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project__id',)


class SectionView(ReadOnlyModelViewSet):
    """Получение всех разделов стратегических задач"""
    serializer_class = SectionSerializer
    queryset = Section.objects.all()


class DepartmentView(ReadOnlyModelViewSet):
    """Получение всех департаментов"""
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()


class ResponsiblePersonView(ReadOnlyModelViewSet):
    """Получение всех различных полных id отвественных"""
    serializer_class = ResponsiblePersonSerializer
    queryset = ResponsiblePerson.objects.distinct("fullname")


class OperationalTaskView(ReadOnlyModelViewSet):
    """
    Получение Опреационных задач
    
    Parameters
    ----------
    strategic_task__id : ID стратегической задачи, по которой осуществляется выборка
    baseline_start_date : Параметр начальной даты
    baseline_finish_date : Параметр конечной даты
    department__id : ID департамента
    responsible_person__fullname : Полное имя отвественного
    status__id : Id статуса
    page : Номер страницы выборки
    """
    serializer_class = SimpleOperationalTaskSerializer
    queryset = OperationalTask.objects.all()
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    pagination_class = PageNumberPagination
    ordering = ['id']

    filterset_fields = {
        'strategic_task__id': ['exact'],
        'department__id': ['exact'],
        'responsible_person__fullname': ['exact'],
        'status__id': ['exact'],
    }

    def get_queryset(self):
        queryset = self.queryset
        baseline_start_date = self.request.query_params.get('baseline_start_date')
        baseline_finish_date = self.request.query_params.get('baseline_finish_date')
        
        if not baseline_start_date or not baseline_finish_date:
            raise BadRequest('baseline_start_date or baseline_finish_date was not found')

        subquery = OperationalTask.objects.filter(
            date__lte=baseline_start_date
        ).order_by(
            'hash_code', "-date"
        ).distinct(
            'hash_code'
        ).values('pk')

        queryset = queryset.filter(
            pk__in=Subquery(subquery)
        ).exclude(status=Statuses.COMPLETED_ON_TIME.value)
        
        if baseline_start_date and baseline_finish_date:
            queryset = queryset.filter(
                (
                    # срок базового начала попал в диапазон
                        Q(baseline_start_date__lte=baseline_start_date) &
                        Q(baseline_finish_date__gte=baseline_start_date)
                ) |
                (
                    # срок актуального начала попал в диапазон
                        Q(start_date__lte=baseline_start_date) &
                        Q(finish_date__gte=baseline_start_date)
                ) |
                (
                    # срок базового окончания попал в диапазон
                        Q(baseline_start_date__lte=baseline_finish_date) &
                        Q(baseline_finish_date__gte=baseline_finish_date)
                ) |
                (
                    # срок базового окончания попал в диапазон
                        Q(start_date__lte=baseline_finish_date) &
                        Q(finish_date__gte=baseline_finish_date)
                ) |
                (
                    # вся задача лежит внутри базового периода
                        Q(baseline_start_date__gte=baseline_start_date) &
                        Q(baseline_finish_date__lte=baseline_finish_date)
                ) |
                (
                    # вся задача лежит внутри фактического периода
                        Q(start_date__gte=baseline_start_date) &
                        Q(finish_date__lte=baseline_finish_date)
                )
            )
        return queryset.distinct()


class StrategicTaskAPIView(generics.ListAPIView):
    """
            Получение стратегических задач

            Parameters
            ----------
            gp__id : Фильтр ГП
            gp__project__id : Фильтр Проект
            gp__project__area__id : Фильтр Регион
            baseline_start_date : Параметр начальной даты. Возвращает значения больше заданного по
            полям start_date/baseline_start_date в операционных задачах
            baseline_finish_date : Параметр конечной даты. Возвращает значения больше заданного по
            полям finish_date/baseline_finish_date в операционных задачах
            section__id : Id раздела
            operational_tasks__department__id : Id департамента
            operational_tasks__responsible_person__fullname : Полное имя отвественного
            operational_tasks__status__id : Id статуса
            """

    serializer_class = StrategicTaskSerializer
    pagination_class = PageNumberPagination

    def process_regular_filter(
            self,
            strategic_task_filter_data,
            operational_task_filter_data,
            baseline_start_date,
            baseline_finish_date,
    ):
        """ Запускает логику фильтрации и отображения последнего snapshot-а"""

        # getting only valid snapshot
        subquery = OperationalTask.objects.filter(
            date__lte=baseline_start_date
        ).order_by(
            'hash_code', "-date"
        ).distinct(
            'hash_code'
        ).values('pk')

        operational_task_queryset = OperationalTask.objects.filter(
            pk__in=Subquery(subquery)
        )

        operational_task_queryset = operational_task_queryset.filter(
            (
                # срок базового начала попал в диапазон
                Q(baseline_start_date__lte=baseline_start_date) &
                Q(baseline_finish_date__gte=baseline_start_date)
            ) |
            (
                # срок актуального начала попал в диапазон
                Q(start_date__lte=baseline_start_date) &
                Q(finish_date__gte=baseline_start_date)
            ) |
            (
                # срок базового окончания попал в диапазон
                Q(baseline_start_date__lte=baseline_finish_date) &
                Q(baseline_finish_date__gte=baseline_finish_date)
            ) |
            (
                # срок базового окончания попал в диапазон
                Q(start_date__lte=baseline_finish_date) &
                Q(finish_date__gte=baseline_finish_date)
            ) |
            (
                # вся задача лежит внутри базового периода
                Q(baseline_start_date__gte=baseline_start_date) &
                Q(baseline_finish_date__lte=baseline_finish_date)
            ) |
            (
                # вся задача лежит внутри фактического периода
                Q(start_date__gte=baseline_start_date) &
                Q(finish_date__lte=baseline_finish_date)
            ),
            **operational_task_filter_data
        ).exclude(
            status=Statuses.COMPLETED_ON_TIME.value,
            strategic_task__status=Statuses.COMPLETED_ON_TIME.value
        ).prefetch_related()

        oper_tasks = list(operational_task_queryset)

        strat_id_on_filter = set()
        for oper_t in oper_tasks:
            strat_id_on_filter.add(oper_t.strategic_task_id)

        # getting only valid snapshot
        subquery = StrategicTask.objects.filter(
            date__lte=baseline_start_date
        ).order_by(
            'hash_code', "-date"
        ).distinct(
            'hash_code'
        ).values('pk')
        
        # has snapshot on period and either has operational or ok with status
        strategic_task_queryset = StrategicTask.objects.filter(
            Q(id__in=tuple(strat_id_on_filter)) |
            Q(**strategic_task_filter_data),
            pk__in=Subquery(subquery)
        ).exclude(status=Statuses.COMPLETED_ON_TIME.value)

        strategic_task_queryset = strategic_task_queryset.prefetch_related(
            Prefetch(
                'operational_tasks', queryset=operational_task_queryset
            )
        )
        return strategic_task_queryset.distinct()

    def get_queryset(self):
        gp_id = self.request.query_params.get('gp__id')
        gp_project_id = self.request.query_params.get('gp__project__id')
        gp_project_area_id = self.request.query_params.get('gp__project__area__id')
        baseline_start_date = self.request.query_params.get('baseline_start_date')
        baseline_finish_date = self.request.query_params.get('baseline_finish_date')
        section_id = self.request.query_params.get('section__id')
        operational_tasks_department_id = self.request.query_params.get(
            'operational_tasks__department__id')
        operational_tasks_responsible_person_fullname = self.request.query_params.get(
            'operational_tasks__responsible_person__fullname')
        operational_tasks_status = self.request.query_params.get('operational_tasks__status__id')

        if not baseline_start_date or not baseline_finish_date:
            raise BadRequest('baseline_start_date or baseline_finish_date was not found')

        strategic_task_filter_data = {
            'is_actual': True,
        }
        operational_task_filter_data = {
            'is_actual': True,
        }

        if gp_id:
            strategic_task_filter_data['gp__id'] = gp_id
            operational_task_filter_data['strategic_task__gp__id'] = gp_id
        if gp_project_id:
            strategic_task_filter_data['gp__project__id'] = gp_project_id
            operational_task_filter_data['strategic_task__gp__project__id'] = gp_project_id
        if gp_project_area_id:
            strategic_task_filter_data['gp__project__area__id'] = gp_project_area_id
            operational_task_filter_data['strategic_task__gp__project__area__id'] = gp_project_area_id
        if section_id:
            strategic_task_filter_data['section__id'] = section_id
            operational_task_filter_data['strategic_task__section__id'] = section_id

        if operational_tasks_department_id:
            strategic_task_filter_data['operational_tasks__department__id'] = operational_tasks_department_id
            operational_task_filter_data['department__id'] = operational_tasks_department_id

        if operational_tasks_responsible_person_fullname:
            strategic_task_filter_data[
                'operational_tasks__responsible_person__fullname'] = operational_tasks_responsible_person_fullname
            operational_task_filter_data['responsible_person__fullname'] = operational_tasks_responsible_person_fullname

        if operational_tasks_status:
            strategic_task_filter_data['status'] = operational_tasks_status
            operational_task_filter_data['status'] = operational_tasks_status
            operational_task_filter_data['strategic_task__status'] = operational_tasks_status

        return self.process_regular_filter(
            strategic_task_filter_data,
            operational_task_filter_data,
            baseline_start_date,
            baseline_finish_date
        )


class StatusesView(APIView):
    """Получение статусов задач"""

    def get(self, request):
        """
        Возвращает список всех статусов
        """
        stuff_statuses = ('COMPLETED_ON_TIME', 'NOT_ACTUAL')
        response = {}
        for status in Statuses:
            status_code_name = status.name
            status_int_value = status.value

            if status_code_name not in stuff_statuses:
                # Служебные статусы, нужные для синка не выдаем в респонс
                response[status_int_value] = status_code_name

        return Response(response)
