---
version: draft
---
Dump to jot down ideas.

- felix writes markdown log files
  - in the style
    - "date", "text", "older date", "text", "older date", "text", ...
  - this could be automated - simply by identifying "sessions"
    - maybe with a sample rate of 4hrs, because
    - can do it manually also
    - sliding window maybe
  - input data would be `(commit_date, line)`
  - must be explicitly enabled by labelling a File with `pdl-postprocs: markdown-log`
  - nice to have: git blame in Sphinx (think blag: "when did I write this?",
    "this is outdated.")
- easy (to implement) schwanzvergleich: how much metadata do you have?
  - inspire hoarding (this is the *lake* in data lake)
  - inspire computation (this is the *data* in data lake; ok, it's more like the
    extract/index step, but hey - it fit)
  - inspire creation of new plugins - the more dimensions you create, the higher
    your score (ps: this scales linearly with the number of dimensions, but
    exponentially with the dynamic creation of further dimensions based on
    existing ones)


SORTME

- vi insert mode cursor color (yellow plz)
- How does one update HTTP headers of a remote resource? What does the standard say about that?
  - How does S3 do it?
    - "When you upload objects using the REST API, the optional user-defined
      metadata names must begin with "x-amz-meta-" to distinguish them from
      other HTTP headers." (bäh)
  - REST framework?
  - minio as target for puddl?
    - `minio sql` https://docs.min.io/docs/minio-client-quickstart-guide.html
    - has k8s and dc deployment
      - [docker-compose deployment][^dc depl] looks clean
  - we will accept any headers matching glob `pdl-$ingress*` and update them
    accordingly [^if-write-perm]

I guess Amazon was a little faster [^faster] in understanding that marrying the
indexing and retrieval of data with HTTP and ROA is a good idea. :>

[^dc depl]: https://raw.githubusercontent.com/minio/minio/master/docs/orchestration/docker-compose/docker-compose.yaml
[^if-write-perm]: RBAC: If user has write permission to the object
[^faster]: 14 years to be exact https://en.wikipedia.org/wiki/Amazon_S3
