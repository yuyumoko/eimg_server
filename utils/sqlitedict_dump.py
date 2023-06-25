from sqlitedict import SqliteDict, SqliteMultithread

CREATE_TABLE_PREFIX = "CREATE TABLE "


def iterdump(sqlite_db: SqliteDict):
    conn: SqliteMultithread = sqlite_db.conn
    yield "BEGIN TRANSACTION;"

    writable_schema = False

    q = """
    SELECT "name", "type", "sql"
    FROM "sqlite_master"
        WHERE "sql" NOT NULL AND
        "type" == 'table'
        ORDER BY "name"
    """
    
    for table_name, type, sql in conn.select(q):
        if table_name == "sqlite_sequence":
            yield ('DELETE FROM "sqlite_sequence";')
        elif table_name == "sqlite_stat1":
            yield ('ANALYZE "sqlite_master";')
        elif table_name.startswith("sqlite_"):
            continue
        elif sql.startswith("CREATE VIRTUAL TABLE"):
            if not writable_schema:
                yield "PRAGMA writable_schema=ON;"
                writable_schema = True
            qtable = table_name.replace("'", "''")
            yield (
                "INSERT INTO sqlite_master(type,name,tbl_name,rootpage,sql) "
                "VALUES('table','{0}','{0}',0,'{1}');"
            ).format(qtable, sql)
            # Skip the bit that writes the INSERTs for this table
            continue
        elif sql.upper().startswith(CREATE_TABLE_PREFIX):
            yield "CREATE TABLE IF NOT EXISTS {};".format(
                sql[len(CREATE_TABLE_PREFIX) :]
            )
        else:
            yield "{0};".format(sql)

        # Build the insert statement for each row of the current table
        table_name_ident = table_name.replace('"', '""')
        res = conn.select('PRAGMA table_info("{0}")'.format(table_name_ident))
        column_names = [str(table_info[1]) for table_info in res]
        q = """SELECT 'INSERT INTO "{0}" VALUES({1})' FROM "{0}";""".format(
            table_name_ident,
            ",".join(
                """'||quote("{0}")||'""".format(col.replace('"', '""'))
                for col in column_names
            ),
        )
        query_res = conn.select(q)
        for row in query_res:
            yield "{0};".format(row[0])

    # Now when the type is 'index', 'trigger', or 'view'
    q = """
    SELECT "name", "type", "sql"
    FROM "sqlite_master"
        WHERE "sql" NOT NULL AND
        "type" IN ('index', 'trigger', 'view')
    """
    schema_res = conn.select(q)
    for name, type, sql in schema_res:
        yield "{0};".format(sql)

    if writable_schema:
        yield "PRAGMA writable_schema=OFF;"

    yield "COMMIT;"
