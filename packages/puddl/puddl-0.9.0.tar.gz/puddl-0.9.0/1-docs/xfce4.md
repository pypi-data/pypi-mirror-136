---
version: draft
---

# xfce4
Set environment for desktop. Also add pyenv's shims to PATH to find the puddl
executable.
```
cat <<'EOF' >> ~/.xprofile
export PUDDL_HOME=~/puddl
export PATH=$PATH:~/.pyenv/shims
EOF
```
https://wiki.archlinux.org/index.php/Xprofile
