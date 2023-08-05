# Notes
anon1234 says:

- venv python3.8 first
- I'm a Fish hipster and need a different README
  - curly brackets don't work in fish --> POSIX compliant installer
  - sourceme must be POSIX
    - felix: maybe "source puddl exports"
  - make sure `export PUDDL_HOME=...` expands `~`


# Storing JSON
Stumbled upon [kinto](https://github.com/Kinto/kinto) while looking for a way to
fix `SADeprecationWarning: The 'postgres' dialect name has been renamed to 'postgresql'`.

[minio](https://min.io/) is my favourite so far. We'll see.


# Postgres Full Text Search
https://www.postgresql.org/docs/9.5/textsearch.html


# Puddl CLI
For now we have this style:
```
puddl PLUGIN ACTION
puddl file ls
puddl file index
puddl file index
```

Having a uniform interface might be a good idea [^fielding].
It also seems to work quite well for kubectl...

## Examples
Index some files
```
find . -type f -name '*.png' | puddl post file
```

List all files [^limit].
```
puddl get file
```

Get all metadata for a concrete file
```
puddl get -oyaml file main.py
```

List all images [^limit]:
```
puddl get file --filter mimetype=image/*
```

Run autolabel on all images
```
puddl get file --output-format=puddl-id --filter mimetype=image/* \
  | puddl post --input-format=puddl-id autolabel
```

## HTTP
Equivalent HTTP requests to the examples above could look like this:
```
GET /file/
GET /file/main.py?pdl-format=yaml

# alternatively as HTTP header, e.g.
GET /file/main.py
Accept: text/yaml

GET /file?mimetype=image/*
```

Query parameters are reserved for apps. This way they have complete flexibility.
The exception are parameters prefixed with `pdl-`.

[^fielding]: https://www.ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm#sec_5_1_5
[^limit]: There should be sane default limits, e.g. 500 as page size(think
  `ORDER BY mtime DESC LIMIT 500`).

### Pipelining
How do we translate a Unix pipeline to HTTP? What is even expected to happen?
```
puddl get file --filter mimetype=image/* --output-format puddl-id \
  | puddl post autolabel
```

We create a resource that will represent the result:
```
POST /autolabel
pdl-source: /file?mimetype=image/*
pdl-backfill: full
```

The server responds with
```
HTTP/2 202 Accepted
pdl-source: /file?mimetype=image/*
pdl-backfill: full
pdl-progress: 1%
Retry-After: 120

<list of processed files here>
```

We can `GET /autolabel/` to get the job's status, which results in a similar
response to the one above. As soon as the processing is done, the server returns
```
HTTP/2 201 Created
pdl-source: /file?mimetype=image/*
pdl-backfill: full
pdl-progress: 100%

<list of processed files here>
```


### Links
- https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
- https://en.wikipedia.org/wiki/List_of_HTTP_header_fields


# Naming
I'm still unhappy with the naming of Ingress, because it is too narrow. For a
tool that does nothing but ETL some data and put it into PG, it's enough, but it
should also provide an interface to query (make sense of) the data.

Unfortunately I don't like the alternatives either:

- Plugin
- Type
- App

All of them are too broad and overloaded. They are simply not specific enough.

The word "puddl" was born from "personal data lake", "PDL" in short, which in
turn could be spelled as "puddle", but searching for "puddle" results in to much
stuff, so I dropped the the "e".
It also fits nicely, because a puddle is a small version of a lake.
Keeping this analogy would be great.


# Elasticsearch
https://github.com/barseghyanartur/django-elasticsearch-dsl-drf

- Elasticsearch DSL = filter, aggregate, define facettes
  - don't need to write ugly JSON by hand
  - basically ORM (Python object --> ES)
- Django Elasticsearch DSL
  - via Meta tags --> convert Django models to ES DSL objects
- django-elasticsearch-dsl-drf
  - integrate Django Elasticsearch DSL with DRF
  - also enables you to use DRF filters
- CON: config hell, but worth it
  - you don't want to NIH
