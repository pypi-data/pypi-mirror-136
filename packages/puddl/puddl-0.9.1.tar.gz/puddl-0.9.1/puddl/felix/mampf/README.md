Add the app and create its schema:
```
puddl app add puddl.felix.mampf
```

Run the server
```
puddl mampf run
```

And POST random stuff
```
curl -d foo=bar http://localhost:5000/something
```

List stuff
```
puddl mampf ls
```


@felix: See also `~/hacks/browserlog/`
