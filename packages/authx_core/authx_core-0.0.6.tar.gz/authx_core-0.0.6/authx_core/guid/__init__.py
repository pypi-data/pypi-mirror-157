"""Python has support for UUIDs in the standard library, and most relational databases
have good support for them as well.
In particular, the postgres-compatible UUID type provided by sqlalchemy (`sqlalchemy.dialects.postgresql.UUID`)
will not work with other databases, and it also doesn't come with a way to set a server-default, meaning that
you'll always need to take responsibility for generating an ID in your application code."""

from authx_core.guid._guide import postgresql as postgresql
from authx_core.guid.type import GUID as GUID
