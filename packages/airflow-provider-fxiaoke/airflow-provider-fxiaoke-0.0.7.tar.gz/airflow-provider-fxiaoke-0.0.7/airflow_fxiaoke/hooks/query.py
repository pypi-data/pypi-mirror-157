"""
Fxiaoke object hooks

create connections:
airflow connections add 'fxiaoke_default' \
    --conn-uri 'fxiaoke://<open_user_id>:<app_secret>@<app_id>:80/<permanent_code>
"""
import sys
import time
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from airflow.exceptions import AirflowException
from airflow.hooks.base import BaseHook
from fxiaoke.api import FxiaokeApi
from fxiaoke.op_query import queryObj as FxiaokeQueryObj
from fxiaoke.op_get import getObj as FxiaokegetObj


class FxiaokeHooks(BaseHook):
    """
    Hooks for Fxiaoke CRM API
    .. seealso::
        For more information on the fxiaoke CRM API, take a look at the API docs:
        https://open.fxiaoke.com/wiki.html
    """
    conn_type = 'fxiaoke'
    conn_name_attr = 'fxiaoke_conn_id'
    default_conn_name = 'fxiaoke_default'
    hook_name = 'Fxiaoke'

    @staticmethod
    def get_connection_form_widgets() -> Dict[str, Any]:
        """Returns connection widgets to add to connection form"""
        from flask_appbuilder.fieldwidgets import BS3TextFieldWidget
        from flask_babel import lazy_gettext
        from wtforms import StringField

        return {
            "extra__fxiaoke__permanent_code": StringField(
                lazy_gettext('PermanentCode'), widget=BS3TextFieldWidget()
            ),
            "extra__fxiaoke__open_user_id": StringField(
                lazy_gettext('OpenUserID'), widget=BS3TextFieldWidget()
            ),
        }

    @staticmethod
    def get_ui_field_behaviour() -> Dict[str, Any]:
        return {
            "hidden_fields": ["port", "host", "schema"],
            "relabeling": {
                "login": "AppID(app_id)",
                "password": "APPSecret(app_secret)",
            },
            "placeholders": {
                'login': 'generate when create app, format: FSAID_xxxxx',
                'password': 'generate when create app',
                'extra__fxiaoke__permanent_code': 'generate when create app',
                'extra__fxiaoke__open_user_id': 'generate when create app, format: FSUID_xxxxxxxxx',
            },
        }

    def __init__(
        self,
        fxiaoke_conn_id: str = default_conn_name,
        api_version: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.fxiaoke_conn_id = fxiaoke_conn_id
        self.api_version = api_version

    def get_conn(self) -> FxiaokeApi:
        """Returns service api"""
        conn = self.get_connection(self.fxiaoke_conn_id)
        self._validate_connection(conn)

        permanent_code = conn.extra_dejson.get(
            'extra__fxiaoke__permanent_code') or conn.extra_dejson.get('permanent_code')
        open_user_id = conn.extra_dejson.get(
            'extra__fxiaoke__open_user_id') or conn.extra_dejson.get('open_user_id')

        self.log.info(
            f'Getting connection using user {open_user_id} for app: {conn.login}.')
        return FxiaokeApi.init(
            app_id=conn.login,
            app_secret=conn.password,
            permanent_code=permanent_code,
            open_user_id=open_user_id,
            api_version=self.api_version,
        )

    def _validate_connection(self, conn: Any) -> None:
        for conn_param in ['login', 'password']:
            if not getattr(conn, conn_param):
                raise AirflowException(
                    f'missing connection parameter {conn_param}')

    def query(
        self,
        object_name: str,
        ds_start_ms: int,
        ds_end_ms: int,
        filter_fileds: str = 'last_modified_time',
        offset: int = 0,
        limit: int = 100,
    ) -> iter:
        api = self.get_conn()
        query = FxiaokeQueryObj(api)
        return query.execute(
            dataObjectApiName=object_name,
            filters=[{
                'field_name': filter_fileds,
                'field_values': [ds_start_ms, ds_end_ms],
                'operator': 'BETWEEN',
            }],
            limit=limit,
            offset=offset
        )

    def get(
        self,
        object_name: str,
        object_id: int,
    ) -> Any:
        api = self.get_conn()
        obj = FxiaokegetObj(api)
        return obj.execute(
            dataObjectApiName=object_name,
            objectDataId=object_id
        )
