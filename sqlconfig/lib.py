import sqlite3
from json import dump as json_dump, load as json_load
import os
import shutil

class UserError(Exception):
    def __init__(self, message, usage=True):
        super().__init__(message)
        self.message = message
        self.usage = usage


def dump(db, dir):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    # first, refuse to dump if any foreign key constraints are violated. unfortunately sqlite's default
    # behavior is to disable foreign key constraints so it's possible that data may have been changed
    # without checking those constraints. In this case we can make sure the data never hits the filesystem.

    c.execute('pragma foreign_key_check')
    num_bad_rows = len(c.fetchall())
    if num_bad_rows > 0:
      raise UserError(str(num_bad_rows) + ' rows failed foreign key integrity checks. Run "pragma foreign_key_check" in the sqlite shell for more information.', False)

    if os.path.exists(dir):
      shutil.rmtree(dir)
    os.makedirs(dir, exist_ok=True)

    # next get the full sql schema
    c.execute('select sql from sqlite_master where name not like "sqlite_%"')
    schema = []
    for (sql,) in c.fetchall():
        if sql is not None:
            schema.append(sql)

    sql_schema = ";\n".join([*schema, ""])
    with open(os.path.join(dir, "schema.sql"), "w") as f:
        f.write(sql_schema)

    # next get all the table names
    c.execute(
        'select name from sqlite_master where type="table" and name not like "sqlite_%"'
    )
    table_names = [name for name, in c.fetchall()]

    for table_name in table_names:
        c.execute("select * from " + table_name + " order by 1 asc")
        rows = []
        for row in c.fetchall():
            dict_row = {}
            for idx, col in enumerate(c.description):
                dict_row[col[0]] = row[idx]
            rows.append(dict_row)

        with open(os.path.join(dir, table_name + ".json"), "w") as f:
            json_dump(rows, f, sort_keys=True, indent=2, separators=(", ", ": "))


def load(db, dir):
    if not os.path.exists(dir):
      # nothing to do
      return
    conn = sqlite3.connect(db)
    c = conn.cursor()
    schema_path = os.path.join(dir, "schema.sql")
    if not os.path.exists(schema_path):
      raise UserError("schema.sql file did not exist in " + dir, False)
    c.execute("pragma foreign_keys=on")
    with open(schema_path, "r") as f:
        c.executescript(f.read())

    c.execute(
        'select name from sqlite_master where type="table" and name not like "sqlite_%"'
    )
    table_names = [name for name, in c.fetchall()]

    for table_name in table_names:
        with open(os.path.join(dir, table_name + ".json"), "r") as f:
            rows = json_load(f)
        for row in rows:
            columns = ", ".join(row.keys())
            placeholders = ":" + ", :".join(row.keys())
            query = "INSERT INTO %s (%s) VALUES (%s)" % (
                table_name,
                columns,
                placeholders,
            )
            try:
                c.execute(query, row)
            except sqlite3.IntegrityError as e:
                raise UserError("IntegrityError inserting row " + repr(row) + " into table " + table_name + ": " + str(e), False)
    conn.commit()