#!/bin/bash
set -euo pipefail

[[ $UID == 0 ]]
uid=$(cut -d: -f1 <<< $RSYNC_USER)
gid=$(cut -d: -f2 <<< $RSYNC_USER)

if ! grep -q ^rsync /etc/group; then
  addgroup \
    -g $gid \
    rsync
fi
if ! grep -q ^rsync /etc/passwd; then
  adduser \
    -h /home/rsync \
    -u $uid \
    -G rsync \
    -D \
    -s /bin/bash \
    rsync
fi

passwd -u rsync 2>/dev/null || true

umask 077

HOST_KEY=/home/rsync/ssh_host_ed25519_key
if [[ ! -f $HOST_KEY ]]; then
  ssh-keygen \
    -f /home/rsync/ssh_host_ed25519_key \
    -N ''\
    -C 'puddl-ingress-rsync'
else
  ssh-keygen -lvf $HOST_KEY
fi

install \
  -d \
  -m 700 \
  -o rsync \
  -g rsync \
  /home/rsync/.ssh
install \
  -o rsync \
  -g rsync \
  -m 600 \
  /tmp/authorized_keys \
  /home/rsync/.ssh/authorized_keys
chmod 700 /home/rsync/.ssh

set -x
exec $@
