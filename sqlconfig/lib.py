import sqlite3
from json import dump as json_dump, load as json_load
import os
import shutil

def dump(db, dir):
    if os.path.exists(dir):
      shutil.rmtree(dir)
    os.makedirs(dir, exist_ok=True)

    conn = sqlite3.connect(db)
    c = conn.cursor()

    # first get the full sql schema
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
    conn = sqlite3.connect(db)
    c = conn.cursor()
    with open(os.path.join(dir, "schema.sql"), "r") as f:
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
            c.execute(query, row)
    conn.commit()