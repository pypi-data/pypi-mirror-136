# TODO
- FIX codimd with new puddl.pg.DB
- REFAC `puddl-felix-*` --> `puddl-*`
  because let's be honest: nobody but me uses this thing 😅
- better ffmpeg using denoise functions https://superuser.com/a/1393535
- `puddl command index` indexes executables on `$PATH`
  - `puddl command ls` lists commands
- use queries from
  https://klotzandrew.com/blog/quickly-debugging-postgres-problems

## improved psql
Improved completion and convenience functions:
```
CREATE OR REPLACE FUNCTION make_into_serial(table_name TEXT, column_name TEXT) RETURNS INTEGER AS $$
DECLARE
    start_with INTEGER;
    sequence_name TEXT;
BEGIN
    sequence_name := table_name || '_' || column_name || '_seq';
    EXECUTE 'SELECT coalesce(max(' || column_name || '), 0) + 1 FROM ' || table_name
            INTO start_with;
    EXECUTE 'CREATE SEQUENCE ' || sequence_name ||
            ' START WITH ' || start_with ||
            ' OWNED BY ' || table_name || '.' || column_name;
    EXECUTE 'ALTER TABLE ' || table_name || ' ALTER COLUMN ' || column_name ||
            ' SET DEFAULT nextVal(''' || sequence_name || ''')';
    RETURN start_with;
END;
$$ LANGUAGE plpgsql VOLATILE;

COMMENT ON FUNCTION make_into_serial IS 'https://stackoverflow.com/a/50568807/241240';
```


# 2022-01
- ORG rename branch "master" to "main"
- REFAC multi-command to minus-separated style to improve shell completion
  - see [1-docs/cli.md]() for motivation
  - `puddl db` --> `puddl-db`
  - `puddl config` --> `puddl-config`
  - click arg handling "inspired by"
    - https://stackoverflow.com/a/50061489/241240
    - https://github.com/pallets/click/issues/108
- BREAKING CHANGE postgres databases instead of schemas
  - schemas always need some wild hacks with `search_path`
  - Django does not work well with schemas [^django-schemas]
  - we can still query different databases using foreign data wrappers
    [^db-fdw]
  - IDEs work more nicely when given a DB connection (I'm looking at you,
    Pycharm Schema selector 🙄)

[^django-scemas]: https://code.djangoproject.com/ticket/6148
[^db-fdw]: https://wiki.postgresql.org/wiki/FAQ#How_do_I_perform_queries_using_multiple_databases.3F


# 2021-10
```
git log --since=2021-02-12 --reverse \
  --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%ai%x08%x08%x08%x08%x08%x08) %C(bold white)<%an>%Creset' \
  --abbrev-commit --stat
```

- `md/` is now called [1-docs/](1-docs/)
- config rewrite
- remove `puddl app ...`
- a few new scripts
  - [bin/puddl-adb-list-packages](bin/puddl-adb-list-packages)
    list packages installed on your mobile device
  - [bin/puddl-adb-wifi](bin/puddl-adb-wifi)
    connect to your mobile device via wifi
  - [bin/puddl-rhymes](bin/puddl-rhymes)
    find rhyming words for German; see [pkgs.Debian](pkgs.Debian)
  - [bin/puddl-audio-duration](bin/puddl-audio-duration)
    audio duration in seconds
  - [bin/puddl-video-timelapse-keyframes](bin/puddl-video-timelapse-keyframes)
    video to timelapse using the stream's key frames; wraps ffmpeg
  - [bin/puddl-adb-contacts](bin/puddl-adb-contacts)
    list contacts; does not work on Android 11 :(
  - [bin/puddl-git-api-documentation-generator](bin/puddl-git-api-documentation-generator)
    Parses git log for `REST API` commit messages and generates API
    documentation. Calling this a draft would be too much. It's more
    of an idea. ;)
- updated [bash startup profiling example](1-docs/bash-profile/)
- sane setup with `setup.cfg`, `pyproject.toml` and [black](https://github.com/psf/black)
- LOTS of stuff in [puddl.felix.exif](puddl/felix/exif/)
  - UI with spacetime data
    - map (space)
    - time (range select at the bottom)
    - data (images on the right)
  - all the refactorings and stuff
  - check `git log -- puddl/felix/exif/`


# 2021-02
- `./bin/audio-remove-silence` using ffmpeg


# 2021-01
- rsync ingress (container) with some scripting
- [Correlating Domain Prefixes with Spam E-Mail](LOG/01-12.md)


# 2020-12
- `puddl db` with consistent `--app` option


# 2020-09
- `puddl json load myapp foo`
  - reads newline-separated lines on STDIN
  - writes to the schema `myapp` into the table `foo`


# 2020-08
- `db.alchemy.App`
- more postgres logging


# 2020-04
- implement a simpler app mechanism
  - apps are simple python modules or packages
  - apps may define a name (default = python package/module name)
  - apps must define a version (semver)
  - apps may write to their tables (i.e. produce)
    - if they do, they must specify them as `writes_to`
  - apps may consume existing tables (i.e. consume)
    - if they do, they must specify them as `reads_from`
- `puddl codimd index` fetches all resources from a codimd instance


# 2020-03
- CLI change: `puddl file index` instead of `puddl file`
- add `puddl file ls` and `puddl file query`
- bash history backfill
- Namespace packages for `puddl.contrib.${plugin-name}`
  - https://packaging.python.org/guides/packaging-namespace-packages/#native-namespace-packages
- flatten CLI
  - plugins live in the same namespace as core commands
  - core commands win
- basic plugin mechanism based on django apps
  - https://docs.djangoproject.com/en/3.0/ref/applications/
  - example plugin "parrot": https://gitlab.com/puddl/parrot

