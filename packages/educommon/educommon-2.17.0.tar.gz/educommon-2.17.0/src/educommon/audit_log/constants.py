# coding: utf-8
from __future__ import absolute_import

import os


# ID блокировок postgresql. Должны быть уникальны в пределах проекта
PG_LOCK_ID = hash('audit_log_lock')


#: Игнорируемые таблицы.
#:
#: Указанные таблицы не отображаются в фильтре столбца "Модель" окна журнала
#: изменений.
EXCLUDED_TABLES = (
    ('public', 'auth_group'),
    ('public', 'auth_group_permissions'),
    ('public', 'auth_permission'),
    ('public', 'auth_user_groups'),
    ('public', 'auth_user_user_permissions'),
    ('public', 'm3_users_assignedrole'),
    ('public', 'm3_users_role'),
    ('public', 'm3_users_rolepermissions'),
)

# Папка с sql файлами
SQL_FILES_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 'sql',
))
