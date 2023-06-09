# Generated by Django 3.2.14 on 2022-08-03 08:47
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
        hash_code='89b6308022943f01588a3bde131d85d5e64cc221'
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
        hash_code='5986d8e3cca8b642c237678e65c6094b4efcbf6b',
    )


def delete_initial_strategic_task(apps, schema_editor):
    Area = apps.get_model('core', 'Area')
    Section = apps.get_model('core', 'Section')
    db_alias = schema_editor.connection.alias
    # Достаточно удалить Регион так как установлен models.CASCADE
    Area.objects.using(db_alias).filter(name=INITIAL_DATA['area_name']).delete()
    Section.objects.using(db_alias).filter(name=INITIAL_DATA['section_name']).delete()


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Район',
                'verbose_name_plural': 'Районы',
            },
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Департамент',
                'verbose_name_plural': 'Департаменты',
            },
        ),
        migrations.CreateModel(
            name='GP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'ГП',
                'verbose_name_plural': 'ГП',
            },
        ),
        migrations.CreateModel(
            name='ResponsiblePerson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fullname', models.CharField(max_length=255, verbose_name='ФИО')),
                ('email', models.CharField(max_length=255, verbose_name='Электронная почта')),
            ],
            options={
                'verbose_name': 'Ответственное лицо',
                'verbose_name_plural': 'Ответственные лица',
                'unique_together': {('fullname', 'email')},
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Раздел стратегической задачи',
                'verbose_name_plural': 'Резделы стратегических задач',
            },
        ),
        migrations.CreateModel(
            name='StrategicTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, null=True, verbose_name='Дата обновления')),
                ('name', models.CharField(max_length=255, verbose_name='Задача')),
                ('start_date', models.DateField(verbose_name='Начало')),
                ('finish_date', models.DateField(verbose_name='Конец')),
                ('actual_finish_date', models.DateField(blank=True, null=True, verbose_name='Актуальный конец')),
                ('baseline_start_date', models.DateField(blank=True, null=True, verbose_name='Плановое начало выполнения')),
                ('baseline_finish_date', models.DateField(blank=True, null=True, verbose_name='Плановое окончание выполнения')),
                ('is_actual', models.BooleanField(verbose_name='Актуальность задачи')),
                ('status', models.IntegerField(choices=[(5, 'Задачи, выполненные в срок, или со сроком исполнения более чем через 30 дней (или их начало и окончание запланировано более чем через 30 дней или на выбранный диапазон'), (10, 'Задачи будущего периода'), (15, 'Задачи на ближайшие 30 дней (которые выполняются сейчас или их начало запланировано на ближайшие 30 дней '), (20, 'Задачи будущего периода, окончание которых прогнозируется с отставанием от базового срока '), (25, 'Неактуальная задача'), (30, 'Задача выполнена не в срок за прошедшие 30 дней '), (35, 'Просроченная не выполненная задача')], verbose_name='Статус')),
                ('hash_code', models.CharField(db_index=True, max_length=255, verbose_name='Хеш код')),
                ('is_display', models.BooleanField(verbose_name='Отображение в графике')),
                ('gp', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='strategic_tasks', to='core.gp', verbose_name='ГП')),
                ('responsible_person', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='strategic_tasks', to='core.responsibleperson', verbose_name='Отвественный')),
                ('section', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='core.section', verbose_name='Раздел')),
            ],
            options={
                'verbose_name': 'Стратегичекская Задача',
                'verbose_name_plural': 'Стратегичекские Задачи',
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='core.area', verbose_name='Район')),
            ],
            options={
                'verbose_name': 'Проект',
                'verbose_name_plural': 'Проекты',
                'unique_together': {('name', 'area')},
            },
        ),
        migrations.CreateModel(
            name='OperationalTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, null=True, verbose_name='Дата обновления')),
                ('name', models.CharField(max_length=255, verbose_name='Задача')),
                ('start_date', models.DateField(verbose_name='Начало')),
                ('finish_date', models.DateField(verbose_name='Конец')),
                ('actual_finish_date', models.DateField(blank=True, null=True, verbose_name='Актуальный конец')),
                ('baseline_start_date', models.DateField(blank=True, null=True, verbose_name='Плановое начало выполнения')),
                ('baseline_finish_date', models.DateField(blank=True, null=True, verbose_name='Плановое окончание выполнения')),
                ('is_actual', models.BooleanField(verbose_name='Актуальность задачи')),
                ('status', models.IntegerField(choices=[(5, 'Задачи, выполненные в срок, или со сроком исполнения более чем через 30 дней (или их начало и окончание запланировано более чем через 30 дней или на выбранный диапазон'), (10, 'Задачи будущего периода'), (15, 'Задачи на ближайшие 30 дней (которые выполняются сейчас или их начало запланировано на ближайшие 30 дней '), (20, 'Задачи будущего периода, окончание которых прогнозируется с отставанием от базового срока '), (25, 'Неактуальная задача'), (30, 'Задача выполнена не в срок за прошедшие 30 дней '), (35, 'Просроченная не выполненная задача')], verbose_name='Статус')),
                ('hash_code', models.CharField(db_index=True, max_length=255, verbose_name='Хеш код')),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.department', verbose_name='Департамент')),
                ('responsible_person', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='operational_tasks', to='core.responsibleperson', verbose_name='Отвественный')),
                ('strategic_task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='operational_tasks', to='core.strategictask', verbose_name='Стратегическая задача')),
            ],
            options={
                'verbose_name': 'Операционная Задача',
                'verbose_name_plural': 'Опреационные Задачи',
            },
        ),
        migrations.AddField(
            model_name='gp',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gps', to='core.project', verbose_name='Проект'),
        ),
        migrations.CreateModel(
            name='ArchivedStrategicTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, null=True, verbose_name='Дата обновления')),
                ('name', models.CharField(max_length=255, verbose_name='Задача')),
                ('start_date', models.DateField(verbose_name='Начало')),
                ('finish_date', models.DateField(verbose_name='Конец')),
                ('actual_finish_date', models.DateField(blank=True, null=True, verbose_name='Актуальный конец')),
                ('baseline_start_date', models.DateField(blank=True, null=True, verbose_name='Плановое начало выполнения')),
                ('baseline_finish_date', models.DateField(blank=True, null=True, verbose_name='Плановое окончание выполнения')),
                ('is_actual', models.BooleanField(verbose_name='Актуальность задачи')),
                ('status', models.IntegerField(choices=[(5, 'Задачи, выполненные в срок, или со сроком исполнения более чем через 30 дней (или их начало и окончание запланировано более чем через 30 дней или на выбранный диапазон'), (10, 'Задачи будущего периода'), (15, 'Задачи на ближайшие 30 дней (которые выполняются сейчас или их начало запланировано на ближайшие 30 дней '), (20, 'Задачи будущего периода, окончание которых прогнозируется с отставанием от базового срока '), (25, 'Неактуальная задача'), (30, 'Задача выполнена не в срок за прошедшие 30 дней '), (35, 'Просроченная не выполненная задача')], verbose_name='Статус')),
                ('hash_code', models.CharField(db_index=True, max_length=255, verbose_name='Хеш код')),
                ('is_display', models.BooleanField(verbose_name='Отображение в графике')),
                ('gp', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='archived_strategic_tasks', to='core.gp', verbose_name='ГП')),
                ('responsible_person', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='archived_strategic_tasks', to='core.responsibleperson', verbose_name='Отвественный')),
                ('section', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='archived_tasks', to='core.section', verbose_name='Раздел')),
            ],
            options={
                'verbose_name': 'Архивная стратегичекская задача',
                'verbose_name_plural': 'Архивные стратегичекские задачи',
            },
        ),
        migrations.CreateModel(
            name='ArchivedOperationalTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, null=True, verbose_name='Дата обновления')),
                ('name', models.CharField(max_length=255, verbose_name='Задача')),
                ('start_date', models.DateField(verbose_name='Начало')),
                ('finish_date', models.DateField(verbose_name='Конец')),
                ('actual_finish_date', models.DateField(blank=True, null=True, verbose_name='Актуальный конец')),
                ('baseline_start_date', models.DateField(blank=True, null=True, verbose_name='Плановое начало выполнения')),
                ('baseline_finish_date', models.DateField(blank=True, null=True, verbose_name='Плановое окончание выполнения')),
                ('is_actual', models.BooleanField(verbose_name='Актуальность задачи')),
                ('status', models.IntegerField(choices=[(5, 'Задачи, выполненные в срок, или со сроком исполнения более чем через 30 дней (или их начало и окончание запланировано более чем через 30 дней или на выбранный диапазон'), (10, 'Задачи будущего периода'), (15, 'Задачи на ближайшие 30 дней (которые выполняются сейчас или их начало запланировано на ближайшие 30 дней '), (20, 'Задачи будущего периода, окончание которых прогнозируется с отставанием от базового срока '), (25, 'Неактуальная задача'), (30, 'Задача выполнена не в срок за прошедшие 30 дней '), (35, 'Просроченная не выполненная задача')], verbose_name='Статус')),
                ('hash_code', models.CharField(db_index=True, max_length=255, verbose_name='Хеш код')),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='archived_operational_tasks', to='core.department', verbose_name='Департамент')),
                ('responsible_person', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='archived_operational_tasks', to='core.responsibleperson', verbose_name='Отвественный')),
                ('strategic_task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='archived_operational_tasks', to='core.archivedstrategictask', verbose_name='Стратегическая задача')),
            ],
            options={
                'verbose_name': 'Архивная операционная задача',
                'verbose_name_plural': 'Архивные операционные задачи',
            },
        ),

        migrations.RunPython(create_superuser, delete_superuser),
        migrations.RunPython(create_initial_strategic_task, delete_initial_strategic_task)
    ]
