import datetime
from typing import Optional, List

from pydantic import BaseModel, fields, validator


class BaseTask(BaseModel):
    name: str = fields.Field(alias='task')
    start_date: datetime.date = fields.Field(alias='start')
    finish_date: datetime.date = fields.Field(alias='finish')
    hash_code: str = fields.Field(alias='hash_code')
    actual_finish_date: Optional[datetime.date] = fields.Field(alias='actual_finish')
    baseline_start_date: Optional[datetime.date] = fields.Field(alias='baseline_start')
    baseline_finish_date: Optional[datetime.date] = fields.Field(alias='baseline_finish')
    date: datetime.date
    is_actual: bool = fields.Field(alias='actual')
    responsible: Optional[str]
    email: Optional[str]
    area: str = fields.Field(alias='city')
    gp: str
    project: str

    def __hash__(self):  # make hashable BaseTask subclass
        return hash(tuple(self.__dict__.values()))

    @validator('responsible')
    def parse_responsible(cls, responsible: Optional[str]):
        if responsible and responsible not in ['None', '', ' ', 'null']:
            return responsible.strip('; ').split(';')[0]
        return None


class OperationalTask(BaseTask):
    department: str
    strat_hash_code: Optional[str] = fields.Field(alias='strat_hash_code')


class Section(BaseModel):
    name: str = fields.Field(alias='task')

    @validator('name')
    def validate_section_name(cls, name: str):
        return name.strip()


class StrategicTask(BaseTask):
    section: str = fields.Field(alias='parent')

    @validator('section')
    def validate_section_name(cls, section_name: str):
        return section_name.strip() or None


class OperationalTaskList(BaseModel):
    operational_tasks: List[OperationalTask]


class StrategicTaskList(BaseModel):
    strategic_tasks: List[StrategicTask]
