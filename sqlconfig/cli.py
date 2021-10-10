import argparse
import os
import sys
import tempfile
import subprocess

from .lib import dump as sql_dump, load as sql_load

class UserError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

def _main():
    parser = argparse.ArgumentParser(
        description="Convert a sqlite database to diffable flat files and back again"
    )
    parser.add_argument(
        "--dump",
        dest="dump",
        action="store_true",
        help="Dump a sqlite db to flat files",
    )
    parser.add_argument(
        "--load",
        dest="load",
        action="store_true",
        help="Load flat files into a new sqlite database",
    )
    parser.add_argument(
        "--shell",
        dest="shell",
        action="store_true",
        help="Load flat files into a temporary database and run the sqlite3 shell"
    )
    parser.add_argument("--db", dest="db", help="sqlite DB to use")
    parser.add_argument("--dir", dest="dir", help="directory to store the flat files")
    parser.add_argument(
        "--overwrite",
        dest="overwrite",
        action="store_true",
        help="whether the flat files can be overwritten",
    )
    args, extra_args = parser.parse_known_args(sys.argv[1:])
    dump = args.dump
    load = args.load
    shell = args.shell
    db = args.db
    dir = args.dir
    overwrite = args.overwrite

    if [dump, load, shell].count(True) != 1:
        raise UserError("One of --dump, --load or --shell must be provided")

    if dir is None:
        raise UserError("--dir must be provided")

    if not shell and db is None:
        raise UserError("--db must be provided")

    if dump:
        if os.path.exists(dir) and not overwrite:
            raise UserError(
                "dir exists, refusing to overwrite without --overwrite flag"
            )

        sql_dump(db, dir)

    if load:
        if os.path.exists(db):
            raise UserError("Refusing to overwrite existing db")
        sql_load(db, dir)

    if shell:
        if db:
            raise UserError("Cannot provide --db and --shell arguments together")

        if not overwrite:
            print('Running shell in read-only mode. Pass --overwrite to save your changes', file=sys.stderr)
        if overwrite:
            print('Running shell in read-write mode.', file=sys.stderr)

        with tempfile.TemporaryDirectory() as tempdir:
            db = os.path.join(tempdir, "db.sql3")
            sql_load(db, dir)
            try:
                subprocess.run(["sqlite3", db, *extra_args])
            finally:
                if overwrite:
                    sql_dump(db, dir)
        

def main():
    try:
        _main()
    except UserError as e:
        print("error:", e.message, file=sys.stderr)
        print("Run with --help for more information.")
        sys.exit(2)

if __name__ == "__main__":
    main()