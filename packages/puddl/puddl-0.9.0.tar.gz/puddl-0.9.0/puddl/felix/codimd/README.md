Add the app and create its schema:
```
puddl app add puddl.felix.codimd
puddl codimd db create
```

Add a remote called `example`
```
puddl db shell <<EOF
INSERT INTO codimd.remotes (name, url, email, password)
VALUES ('example', 'https://codimd.example.org', 'alice@example.org', 'secret');
EOF
```
