from sqlalchemy_dialects.es.exceptions import (
    DatabaseError,
    DataError,
    Error,
    IntegrityError,
    InterfaceError,
    InternalError,
    NotSupportedError,
    OperationalError,
    ProgrammingError,
    Warning,
)
from .api import connect


__all__ = [
    "connect",
    "apilevel",
    "threadsafety",
    "paramstyle",
    "DataError",
    "DatabaseError",
    "Error",
    "IntegrityError",
    "InterfaceError",
    "InternalError",
    "NotSupportedError",
    "OperationalError",
    "ProgrammingError",
    "Warning",
]


apilevel = "2.0"
# Threads may share the module and connections
threadsafety = 2
paramstyle = "pyformat"
