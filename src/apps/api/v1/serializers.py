from rest_framework import serializers
from constance import config

from apps.core.models import Area, Department, GP, OperationalTask, Project, \
    ResponsiblePerson, Section, StrategicTask


class AreaSerializer(serializers.ModelSerializer):
    """ Сериализатор для модели "Район" """

    class Meta:
        model = Area
        fields = ["name", "id"]


class ProjectWithoutAreaSerializer(serializers.ModelSerializer):
    """ Сериализатор для модели "Проект" без вложенных полей"""

    class Meta:
        model = Project
        fields = ["name", "id"]


class ProjectSerializer(serializers.ModelSerializer):
    """ Сериализатор для модели "Проект" """
    area = AreaSerializer()

    class Meta:
        model = Project
        fields = "__all__"


class GPWithoutProjectSerializer(serializers.ModelSerializer):
    """ Сериализатор для модели "ГП"
        Схема нужна для предоставления сериализации ProjectSerializer
    """

    class Meta:
        model = GP
        fields = ["name", "id"]


class ProjectWithGPsSerializer(serializers.ModelSerializer):
    """ Сериализатор для модели "Проект"
        Схема нужна для предоставления сериализации GPSerializer
    """

    area = AreaSerializer()
    gp = GPWithoutProjectSerializer(many=True)

    class Meta:
        model = Project
        fields = ["area", "name", "gp"]


class GPSerializer(serializers.ModelSerializer):
    """ Сериализатор для модели "ГП" """

    project = ProjectSerializer()

    class Meta:
        model = GP
        fields = "__all__"


class DepartmentSerializer(serializers.ModelSerializer):
    """ Сериализатор для модели "Департамент" """

    class Meta:
        model = Department
        fields = "__all__"


class ResponsiblePersonSerializer(serializers.ModelSerializer):
    """ Сериализатор для модели "Ответственное лицо" """

    class Meta:
        model = ResponsiblePerson
        fields = ['fullname']


class SectionSerializer(serializers.ModelSerializer):
    """ Сериализатор для модели "Раздел страт задачи" """

    class Meta:
        model = Section
        fields = "__all__"


class SimpleOperationalTaskSerializer(serializers.ModelSerializer):
    """ Сериализатор для модели "Операционная задача"
        Схема нужна для предоставления сериализации StrategicTaskSerializer
    """

    responsible_person = ResponsiblePersonSerializer()
    department = DepartmentSerializer()

    class Meta:
        model = OperationalTask
        exclude = ["hash_code", "strategic_task"]


class StrategicTaskSerializer(serializers.ModelSerializer):
    """ Сериализатор для модели "Стратегическая задача" """

    responsible_person = ResponsiblePersonSerializer()
    gp = GPSerializer()
    section = SectionSerializer()
    operational_tasks = serializers.SerializerMethodField(required=False, read_only=True)

    @staticmethod
    def get_operational_tasks(obj):
        return SimpleOperationalTaskSerializer(
            obj.operational_tasks.all()[:config.MAX_OPERATIONAL_TASK_ON_STRATEGIC_TASK], many=True
        ).data

    class Meta:
        model = StrategicTask
        exclude = ["hash_code"]


class SimpleStrategicTaskSerializer(serializers.ModelSerializer):
    """ Сериализатор для модели "Стратегическая задача"
        Схема нужна для предоставления сериализации OperationalTaskSerializer
    """

    responsible_person = ResponsiblePersonSerializer()
    gps = GPSerializer()
    section = SectionSerializer()

    class Meta:
        model = StrategicTask
        exclude = ["hash_code"]


class OperationalTaskSerializer(serializers.ModelSerializer):
    """ Сериализатор для модели "Операционная задача" """

    responsible_person = ResponsiblePersonSerializer(many=True)
    department = DepartmentSerializer()

    strategic_task = SimpleStrategicTaskSerializer()

    class Meta:
        model = OperationalTask
        exclude = ["hash_code"]
