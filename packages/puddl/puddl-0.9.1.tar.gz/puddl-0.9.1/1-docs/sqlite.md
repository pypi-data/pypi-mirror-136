# sqlite
Maybe we can replace Postgres with sqlite.

## Why?
- simple backup/restore (cp)
- ubiquitous

## JSON
- https://www.sqlite.org/json1.html

The json1 extension is compiled for sqlite3 on Ubuntu 20.04:
```
$ echo "PRAGMA compile_options;" | sqlite3 | grep JSON1
ENABLE_JSON1
```
