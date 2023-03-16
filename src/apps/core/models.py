import datetime
import json
from typing import Optional

from constance import config
from django.db import models
from django.db.models import F, Q

INITIAL_DATA = json.loads(config.INITIAL_DATA_NAMES.replace("'", "\""))


class Area(models.Model):
    """Район работы"""

    name = models.CharField(
        verbose_name="Название",
        max_length=255,
        unique=True,
    )

    class Meta:
        verbose_name = "Район"
        verbose_name_plural = "Районы"

    def __str__(self):
        return f'{self.name}'


class Project(models.Model):
    """Проект"""

    name = models.CharField(
        verbose_name="Название",
        max_length=255,
    )
    area = models.ForeignKey(
        "core.Area",
        verbose_name="Район",
        related_name="projects",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        unique_together = ('name', 'area')

    def __str__(self):
        return f'{self.name}'


class GP(models.Model):
    """	ГП """

    name = models.CharField(
        verbose_name="Название",
        max_length=255,
    )
    project = models.ForeignKey(
        "core.Project",
        verbose_name="Проект",
        related_name="gps",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "ГП"
        verbose_name_plural = "ГП"

    def __str__(self):
        return f'{self.name}'


class Department(models.Model):
    """	Департамент	"""

    name = models.CharField(
        verbose_name="Название",
        max_length=255,
    )

    class Meta:
        verbose_name = "Департамент"
        verbose_name_plural = "Департаменты"

    def __str__(self):
        return f'{self.name}'


class ResponsiblePerson(models.Model):
    """Ответственное лицо"""

    fullname = models.CharField(
        verbose_name="ФИО",
        max_length=255,
    )
    email = models.CharField(
        verbose_name="Электронная почта",
        max_length=255,
    )

    class Meta:
        verbose_name = "Ответственное лицо"
        verbose_name_plural = "Ответственные лица"
        unique_together = ("fullname", "email")

    def __str__(self):
        return f'{self.fullname}'


class Section(models.Model):
    """ Раздел стратегической задачи"""

    name = models.CharField(
        verbose_name="Название",
        max_length=255,
        unique=True,
    )

    class Meta:
        verbose_name = "Раздел стратегической задачи"
        verbose_name_plural = "Резделы стратегических задач"

    def __str__(self):
        return f'{self.name}'


class Statuses(models.IntegerChoices):
    COMPLETED_ON_TIME = 5, 'Задачи, выполненные в срок (5)'
    FUTURE_TASK = 10, 'Задачи выполняется в срок более 30 дней (10)'
    IN_PROGRESS = 15, 'Выполняется (15)'
    OVERDUE_RISK = 20, 'Прогноз отставания от графика (20)'
    NOT_ACTUAL = 25, 'Неактуальная задача (25)'
    OVERDUE_BY_DEADLINE = 30, 'Выполнена с отсрочкой (30)'
    OVERDUE = 35, 'Просрочено, не выполнено (35)'


class Task(models.Model):
    date = models.DateField(
        verbose_name='Дата обновления',
        null=True, blank=True
    )
    name = models.CharField(
        verbose_name="Задача",
        max_length=255,
    )
    start_date = models.DateField(
        verbose_name="Начало"
    )
    finish_date = models.DateField(
        verbose_name="Конец"
    )
    actual_finish_date = models.DateField(
        verbose_name="Актуальный конец",
        null=True,
        blank=True
    )
    baseline_start_date = models.DateField(
        verbose_name="Плановое начало выполнения",
        null=True,
        blank=True
    )
    baseline_finish_date = models.DateField(
        verbose_name="Плановое окончание выполнения",
        null=True,
        blank=True
    )
    is_actual = models.BooleanField(
        verbose_name="Актуальность задачи"
    )
    status = models.IntegerField(
        verbose_name='Статус',
        choices=Statuses.choices,
    )
    hash_code = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name='Хеш код',
    )

    class Meta:
        abstract = True
        constraints = [
            models.CheckConstraint(
                check=Q(finish_date__gte=F('start_date')),
                name='operational_check_start_end_date'
            )
        ]
        unique_together = ['source_id', 'date']


class OperationalTask(Task):
    """	Операционная Задача """

    department = models.ForeignKey(
        "core.Department",
        verbose_name="Департамент",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    responsible_person = models.ForeignKey(
        "core.ResponsiblePerson",
        verbose_name="Отвественный",
        related_name="operational_tasks",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    strategic_task = models.ForeignKey(
        "core.StrategicTask",
        verbose_name="Стратегическая задача",
        related_name="operational_tasks",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Операционная Задача"
        verbose_name_plural = "Операционные Задачи"

    def __str__(self):
        return f'{self.name}'

    @staticmethod
    def get_strategic_task(strategic_task_source_id: Optional[int]):
        return StrategicTask.objects.filter(
            source_id=strategic_task_source_id
        ).first() or StrategicTask.objects.filter(
            name=INITIAL_DATA['strategic_task_name']
        ).first()

    @staticmethod
    def get_strategic_task_for_hash_code(hash_code: Optional[str], dt: datetime.date) -> 'StrategicTask':
        return StrategicTask.objects.filter(
            hash_code=hash_code
        ).order_by('-date').first() or StrategicTask.objects.filter(
            name=INITIAL_DATA['strategic_task_name']
        ).first()


class ArchivedOperationalTask(Task):
    """	Операционная задача в архиве"""

    department = models.ForeignKey(
        "core.Department",
        verbose_name="Департамент",
        related_name='archived_operational_tasks',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    responsible_person = models.ForeignKey(
        "core.ResponsiblePerson",
        verbose_name="Отвественный",
        related_name="archived_operational_tasks",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    strategic_task = models.ForeignKey(
        "core.ArchivedStrategicTask",
        verbose_name="Стратегическая задача",
        related_name="archived_operational_tasks",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Архивная операционная задача"
        verbose_name_plural = "Архивные операционные задачи"

    def __str__(self):
        return f'{self.name}'

    @staticmethod
    def get_archived_strategic_task(strategic_task_source_id: Optional[int]):
        return ArchivedStrategicTask.objects.filter(
            source_id=strategic_task_source_id
        ).first() or ArchivedStrategicTask.objects.filter(
            name=INITIAL_DATA['archived_strategic_task_name']
        ).first()


class StrategicTask(Task):
    """	Стратегическая задача """

    gp = models.ForeignKey(
        "core.GP",
        verbose_name="ГП",
        related_name="strategic_tasks",
        on_delete=models.CASCADE,
    )
    section = models.ForeignKey(
        "core.Section",
        verbose_name="Раздел",
        related_name="tasks",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    responsible_person = models.ForeignKey(
        "core.ResponsiblePerson",
        verbose_name="Отвественный",
        related_name="strategic_tasks",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    is_display = models.BooleanField(
        verbose_name="Отображение в графике",
    )

    class Meta:
        verbose_name = "Стратегичекская Задача"
        verbose_name_plural = "Стратегичекские Задачи"

    def __str__(self):
        return f'{self.name}'


class ArchivedStrategicTask(Task):
    """	Архивная стратегическая задача """

    gp = models.ForeignKey(
        "core.GP",
        verbose_name="ГП",
        related_name="archived_strategic_tasks",
        on_delete=models.CASCADE,
    )
    section = models.ForeignKey(
        "core.Section",
        verbose_name="Раздел",
        related_name="archived_tasks",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    responsible_person = models.ForeignKey(
        "core.ResponsiblePerson",
        verbose_name="Отвественный",
        related_name="archived_strategic_tasks",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    is_display = models.BooleanField(
        verbose_name="Отображение в графике",
    )

    class Meta:
        verbose_name = "Архивная стратегичекская задача"
        verbose_name_plural = "Архивные стратегичекские задачи"

    def __str__(self):
        return f'{self.name}'
