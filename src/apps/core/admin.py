import json
from django.contrib import admin
from django.db.models import Count
from django_admin_inline_paginator.admin import TabularInlinePaginated
from django.utils.translation import gettext_lazy as _
from constance import config

from .models import (
    Project,
    Area,
    GP,
    Department,
    ResponsiblePerson,
    Section,
    OperationalTask,
    StrategicTask,
)

INITIAL_DATA = json.loads(config.INITIAL_DATA_NAMES.replace("'", "\""))


class ProjectInLine(TabularInlinePaginated):
    verbose_name = 'Проект'
    verbose_name_plural = 'Проекты'
    model = Project
    per_page = 10
    extra = 0


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = (
        "name",
    )

    inlines = (
        ProjectInLine,
    )


class GPInLine(TabularInlinePaginated):
    verbose_name = 'Проект'
    verbose_name_plural = 'Проекты'
    per_page = 10
    model = GP
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
    )

    inlines = (
        GPInLine,
    )


@admin.register(GP)
class GPAdmin(admin.ModelAdmin):
    list_display = (
        "name",
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
    )


@admin.register(ResponsiblePerson)
class ResponsiblePersonAdmin(admin.ModelAdmin):
    list_display = (
        "fullname",
        "email",
    )


class StrategicTaskInLine(TabularInlinePaginated):
    verbose_name = 'Стратегические задачи'
    verbose_name_plural = 'Стратегические задачи'
    per_page = 10
    model = StrategicTask
    extra = 0


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "task_count"
    )

    inlines = (
        StrategicTaskInLine,
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            tasks_count=Count('tasks')
        )

    @admin.display(description='Количество стратегических задач')
    def task_count(self, obj: Section) -> int:
        return obj.tasks.count()

    task_count.admin_order_field = 'tasks_count'


class RelatedStrategicTaskFilter(admin.SimpleListFilter):
    title = _('Неопределенная стратегическая задача')
    parameter_name = 'indefinite'

    def lookups(self, request, model_admin):
        return (
            ('True', _('Да')),
            ('False', _('Нет')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(strategic_task__name=INITIAL_DATA['strategic_task_name'])
        if self.value() == 'False':
            return queryset.exclude(strategic_task__name=INITIAL_DATA['strategic_task_name'])


@admin.register(OperationalTask)
class OperationalTaskAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "date",
        "hash_code",
        "is_actual",
        "responible_person",
        'strategic_task',
        'status',
    )
    search_fields = ('id',)
    readonly_fields = ('hash_code',)
    list_filter = (
        RelatedStrategicTaskFilter, 'is_actual', 'department', 'status',
        'strategic_task__gp__name', 'strategic_task__gp__project__name',
        'strategic_task__gp__project__area__name', 'strategic_task__section__name',
    )

    def responible_person(self, obj):
        return obj.responsible_person

    responible_person.short_description = "Ответсвенные лица"

    def get_search_results(self, request, queryset, search_term):
        search_words = search_term.split('&')
        super_search_term = ''
        if search_words:
            for word in search_words:
                split_word = word.split('=')
                if len(split_word) > 1:
                    if split_word[0] == 'name':
                        queryset = queryset.filter(name=split_word[1])
                    elif split_word[0] == 'strategic_task':
                        queryset = queryset.filter(strategic_task__name=split_word[1])
                    elif split_word[0] == 'date':
                        queryset = queryset.filter(date__lte=split_word[1]).order_by(
                            'hash_code', "-date"
                        ).distinct('hash_code')
                else:
                    super_search_term += '='.join(split_word)
        return super().get_search_results(request, queryset, super_search_term)


class OperationalTaskInLine(TabularInlinePaginated):
    verbose_name = 'Операционная задача'
    verbose_name_plural = 'Операционные задачи'
    per_page = 10
    model = OperationalTask
    extra = 0


@admin.register(StrategicTask)
class StrategicTaskAdmin(admin.ModelAdmin):
    list_display = (
        "name", "date", "hash_code", "is_actual",
        "responsible_person", 'section', 'status'
    )
    list_filter = (
        'is_actual', 'status', 'section', 'gp__name', 'gp__project', 'gp__project__area',
    )
    search_fields = ('id',)
    readonly_fields = ('hash_code',)

    def get_search_results(self, request, queryset, search_term):
        search_words = search_term.split('&')
        super_search_term = ''
        if search_words:
            for word in search_words:
                split_word = word.split('=')
                if len(split_word) > 1:
                    if split_word[0] == 'name':
                        queryset = queryset.filter(name=split_word[1])
                    elif split_word[0] == 'date':
                        queryset = queryset.filter(date__lte=split_word[1]).order_by(
                            'hash_code', "-date"
                        ).distinct('hash_code')
                else:
                    super_search_term += '='.join(split_word)
        return super().get_search_results(request, queryset, super_search_term)

    inlines = (
        OperationalTaskInLine,
    )
