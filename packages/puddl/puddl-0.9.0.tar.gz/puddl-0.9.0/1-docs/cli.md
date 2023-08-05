# Command Line Interface
Puddl commands start with the prefix `puddl-` followed by something, e.g.
`puddl-config`, `puddl-db`, `puddl-git`, ...

Why not use `puddl something` instead? Simply because `pud<TAB>` should expand
to `puddl-`.

This makes it trivial to add new commands that get **auto completion** for
free, e.g.
```
cat <<'EOF' > ~/bin/puddl-new-command
#!/bin/bash
echo 'Hello World!'
EOF
chmod +x ~/bin/puddl-new-command
```
