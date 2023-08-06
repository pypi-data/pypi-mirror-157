import json

# from sqlalchemy.event import listen
from typing import Optional

import fastapi as fastapi
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy.engine import _after_cur_exec, _handle_error
from opentelemetry.instrumentation.utils import _generate_sql_comment
from opentelemetry.sdk.resources import Attributes
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from sqlalchemy import event
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor, EngineTracer

from fastapialchemycollector import PlanCollectType
from fastapialchemycollector.consts import (
    METIS_DO_NOT_TRACK_COMMENT,
    METIS_STATEMENT_SPAN_ATTRIBUTE,
    METIS_PLAN_SPAN_ATTRIBUTE,
)
from fastapialchemycollector.instruments import EXPLAIN_SUPPORTED_STATEMENTS
from opentelemetry.trace import Span
from sqlalchemy import event

INSTRUMENTING_LIBRARY_VERSION = '0.30b1'


def add_quote_to_value_of_type_string(value):
    if isinstance(value, str):
        new_value = str(value).replace("'", "''")
        return "'{}'".format(new_value)  # pylint: disable=consider-using-f-string
    return value


def fix_sql_query(sql, params):
    """without the fix the query is not working because string is not quoted"""
    fixed_param = params
    if isinstance(params, dict):
        fixed_param = {
            key: add_quote_to_value_of_type_string(value)
            for key, value in params.items()
        }

    return sql % fixed_param


class MetisFastAPIInstrumentor(FastAPIInstrumentor):

    def _uninstrument(self, **kwargs):
        super()._uninstrument(**kwargs)
        FastAPIInstrumentor.uninstrument_app(fastapi.FastAPI)