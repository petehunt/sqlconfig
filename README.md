# sqlconfig: manage your config files with sqlite

## The problem

Your app probably has a lot of configuration in git. Storing it as files in a git repo has a lot of advantages, including:

- Diffing
- Rollbacks
- Blame
- Branching

However, flat files in a repo can get unwieldy:

- Different files need to be kept in sync with each other
- Bulk operations are challenging
- It's easy to add invalid data
- They're disorganized

`sqlconfig` gives you all the advantages of config files stored in version control, with the power, flexibility and safety of SQL.

## The solution

Model your config as a SQLite database. `sqlconfig` can deterministically turn that database into diffable flat files that live in the repo and back again.

## Tutorial

Install sqlconfig. You need Python 3.

```
$ pip install sqlconfig
```

Next, design your config in SQLite. For this example, we'll use Twitch's [unfairly ridiculued spam system](https://news.ycombinator.com/item?id=28821376).

```
$ sqlconfig --shell --dir example_config --overwrite
Running shell in read-write mode.
SQLite version 3.31.1 2020-01-27 19:55:54
Enter ".help" for usage hints.
sqlite> create table keyword_categories (id integer primary key, name text not null unique);
sqlite> create table keywords (id integer primary key, category_id integer not null references keyword_categories(id), keyword text unique);
sqlite> insert into keyword_categories (name) values ("spam"),("hate"),("false_positives");
sqlite> insert into keywords (category_id, keyword) values (1, "viagra"),(1, "nigerian prince"),(2, "suck"),(2, "jerk"),(3, "fanny hands lane");
```

We can see that sqlconfig has created files on disk:

```
$ ls example_config/
keyword_categories.json  keywords.json  schema.sql
```

Note that the JSON files are printed deterministically and in a format that's easy for `git diff` to work with.

Note one of the advantages of using SQL is that it's harder to write a bad config. For example, if we delete a keyword category without deleting all the keywords in it, we get an error.

```
$ sqlconfig --shell --dir example_config --overwrite
Running shell in read-write mode.
SQLite version 3.31.1 2020-01-27 19:55:54
Enter ".help" for usage hints.
sqlite> delete from keyword_categories where id=1;
sqlite>
error: 2 rows failed foreign key integrity checks. Run "pragma foreign_key_check" in the sqlite shell for more information.
```

### Reading your config

It's recommended to put your `schema.sql` and `.json` files in a git repository and to review changes to them as part of your normal code review or pull request process. Through CI, you can publish this repo to your configuration management system of choice.

If you don't want to read the files directly, you can also read them with SQL. Either via the command line:

```
$ sqlconfig --shell --dir example_config -- -header -csv 'select keyword from keywords where category_id=1'
Running shell in read-only mode. Pass --overwrite to save your changes
keyword
viagra
"nigerian prince"
```

or by exporting a SQLite database to disk with `--load` and reading it from your application or another tool.

```
$ sqlconfig --load --db config.sqlite --dir example_config
$ sqlite3 config.sqlite -header -csv 'select keyword from keywords where category_id=1'
keyword
viagra
"nigerian prince"
```

### Best practices

It's best to put the `schema.sql` and `<table>.json` files in a git repo, and use a CI job to push the config to whatever system should serve it. Before doing so, it's a good idea to use `sqlconfig` to validate the configuration:

```
$ sqlconfig --check --dir example_config/
OK
```

## API

You can use `sqlconfig.lib.load(db, dir)` and `sqlconfig.lib.dump(db, dir)` to programmatically perform these operations. Read the code if you have any questions :)
