import sqlalchemy as sa


def postgresql(engine: sa.engine.Engine) -> None:  # pragma: no cover
    """
    Set up UUID generation using the pgcrypto extension for postgres
    This query only needs to be executed once when the database is created

    import sqlalchemy as sa
    from authx_core import postgresql

    database_url = "postgresql://user:password@db:5432/app"
    engine = sa.create_engine(database_url)
    postgresql(engine)
    """
    engine.execute('create EXTENSION if not EXISTS "pgcrypto"')
