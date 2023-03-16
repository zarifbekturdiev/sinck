import datetime
from typing import Optional

from django.db import connections
from django.db.backends.utils import CursorDebugWrapper
from constance import config


class TaskFetcher:
    cursor: CursorDebugWrapper

    def __init__(self):
        self.cursor = connections['source'].cursor()

    def close_cursor(self):
        self.cursor.close()

    def get_last_upgrade_date(self, table_name: str, last_sync_date: Optional[datetime.date]) -> str:
        """
            Возвращает дату последнего обновления данных.
        """
        if last_sync_date:
            return last_sync_date.strftime('%Y-%m-%d')
        self.cursor.execute(f"SELECT date FROM {table_name} ORDER BY date DESC LIMIT 1")
        dt: datetime.date = self.cursor.fetchone()[0]
        return dt.strftime('%Y-%m-%d')

    def get_cursor_for_sections(self, last_sync_date: Optional[datetime.date]):
        date_str: str = self.get_last_upgrade_date(
            config.STRATEGIC_SOURCE_TABLENAME, last_sync_date
        )
        query = f"SELECT DISTINCT task, id_do FROM {config.STRATEGIC_SOURCE_TABLENAME} " \
                f"WHERE (date = '{date_str}' AND id_do is not null AND (parent IS NULL OR parent = ''));"
        self.cursor.execute(query)
        return self.cursor

    def get_cursor_for_strategic_tasks(
            self, last_sync_date: Optional[datetime.date]
    ) -> CursorDebugWrapper:
        """
            Возвращает Cursor для получение стратегических задач
        """
        date_str: str = self.get_last_upgrade_date(
            config.STRATEGIC_SOURCE_TABLENAME, last_sync_date
        )
        query = f"SELECT *, sha1(CONCAT(task, gp, project, city)) as hash_code FROM {config.STRATEGIC_SOURCE_TABLENAME} " \
                f"WHERE (date = '{date_str}' AND id_do is not null AND " \
                f"city IS NOT NULL AND gp IS NOT NULL AND project IS NOT NULL AND " \
                f"id_do_parent IS NOT NULL AND parent IS NOT NULL AND parent != '' AND " \
                f"start IS NOT NULL AND finish IS NOT NULL);"
        self.cursor.execute(query)
        return self.cursor

    def get_cursor_for_operational_tasks(
            self, last_sync_date: Optional[datetime.date]
    ) -> CursorDebugWrapper:
        """
            Возвращает операционные задачи
        """
        date_str: str = self.get_last_upgrade_date(
            config.OPERATIONAL_SOURCE_TABLENAME, last_sync_date
        )
        query = f"SELECT *, sha1(CONCAT(task, gp, project, city)) as hash_code, " \
                f"(CASE " \
                f"WHEN (strat_name is not null and strat_name != '') THEN sha1(CONCAT(strat_name, gp, project, city)) " \
                f"ELSE null END) as strat_hash_code " \
                f"FROM {config.OPERATIONAL_SOURCE_TABLENAME} " \
                f"WHERE (date = '{date_str}' AND id_do is not null AND " \
                f"city IS NOT NULL AND gp IS NOT NULL AND project IS NOT NULL AND " \
                f"start IS NOT NULL AND finish IS NOT NULL);"
        self.cursor.execute(query)
        return self.cursor
