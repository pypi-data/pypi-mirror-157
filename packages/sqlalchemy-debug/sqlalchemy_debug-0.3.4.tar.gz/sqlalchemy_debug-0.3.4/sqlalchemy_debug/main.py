import sys
from sqlalchemy.orm.query import Query
from sqlalchemy.sql.dml import Insert, Update, Delete
from sqlalchemy.sql.selectable import Select
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from sqlalchemy.sql.schema import Table
from sqlalchemy.schema import CreateTable
from sqlalchemy.engine.default import DefaultDialect
from sqlalchemy.sql.sqltypes import String, DateTime, NullType
PY3 = sys.version_info[0] == 3
text = str if PY3 else unicode
int_type = int if PY3 else (int, long)
str_type = str if PY3 else (str, unicode)


class StringLiteral(String):
    def literal_processor(self, dialect):
        super_processor = super(StringLiteral, self).literal_processor(dialect)

        def process(value):
            if isinstance(value, int_type):
                return text(value)
            elif not isinstance(value, str_type):
                value = text(value)
            result = super_processor(value)
            if isinstance(result, bytes):
                result = result.decode(dialect.encoding)
            return result

        return process


class LiteralDialect(DefaultDialect):
    colspecs = {
        String: StringLiteral,
        DateTime: StringLiteral,
        NullType: StringLiteral
    }


def _compile_statement(smt):
    _smt = smt.compile(dialect=LiteralDialect(), compile_kwargs={"literal_binds": True})
    return _smt


def debug_statement(q, need_parameter=True):
    if isinstance(q, DeclarativeMeta):
        if hasattr(q, "__table__"):
            return str(CreateTable(q.__table__))
    elif isinstance(q, Table):
        return str(CreateTable(q))
    elif isinstance(q, Query):
        if need_parameter:
            smt = q.statement
            smt = _compile_statement(smt)
            return str(smt)
    elif isinstance(q, Insert):
        if need_parameter:
            param = q.parameters
            return str(q), param
    elif isinstance(q, (Select, Update, Delete)):
        smt = _compile_statement(q)
        return str(smt)
    else:
        return str(q)