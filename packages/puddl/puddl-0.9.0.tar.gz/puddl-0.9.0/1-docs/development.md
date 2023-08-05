---
version: draft
---

# Personas and Stuff
- hostnames: philosophers
  - must have ASCII characters only, e.g. plato, socrates, epictetus
  - should be recognizable
- users: alice, bob, charlie, mallory
- projects: fooproject, barproject, ...


# Source, Ingress, Stream
A Source is a device that created a Stream, e.g.

- the notebook called `f`"
- the mobile phone called `s7`
- the server called `s3`
- the camera called `gopro-1`

An Ingress contains the logic to create a Stream from a Source. You may think of
it as the "stream type". The `stdin/v1` Ingress for example can consume STDIN
and create a Stream from that. The `git/commit/v1` can be used to stream
git commits.

A Stream is some concrete data. It always has a date and an ID. To be useful it
probably has some data, for example a video file or something you wrote. See
[ingress.md](ingress.md) for more examples.
Streams also have meta data stored as JSON objects. This way you can provide a
lot of context for a Stream.

## NotImplementedError('README-driven-development')

Let's take the `git/commit/v1` Ingress as an example. First, initialize the
ingress to make it available to puddl:
```
puddl initialize git/commit/v1
```

Now puddl can make use of the ingress subcommand `git/commit/v1`. This also
creates the alias `git/commit`, because `v1` is the only, and thus latest,
version. Special to the `git/commit` Ingress is that it must be initialized in a
git repository. Under the hood it creates a post-commit hook.
```
cd ~/some-repo
puddl init git/commit
```

Whenever you commit something in `~/some-repo`, the diff is saved ...

-- Why though? We don't need to save the diff! All we need to do is save the
meta data and create a URI. The last part could become a bit tricky. ^^
