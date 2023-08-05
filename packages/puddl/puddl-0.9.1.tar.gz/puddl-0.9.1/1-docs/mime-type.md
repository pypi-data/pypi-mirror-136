# MIME Type


## Name
`application/prs.puddl`, because it's application data and it's **personal**
[^prs].

[^prs]: https://en.wikipedia.org/wiki/Media_type#Personal_or_vanity_tree


## Install MIME Type on systems that are freedesktop.org compliant
```
sudo -i
cat <<EOF > /usr/share/mime/packages/puddl.xml 
<?xml version="1.0" encoding="UTF-8"?>
<mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">
   <mime-type type="application/prs.puddl">
     <comment>puddl</comment>
     <glob pattern="*.pdl"/>
   </mime-type>
</mime-info>
EOF

update-mime-database /usr/share/mime/
exit
```
https://unix.stackexchange.com/a/103982


## URL Protocol Handler
```
cat <<EOF > ~/.local/share/applications/puddl-puddl.desktop
[Desktop Entry]
Type=Application
Name=puddl
Exec=puddl-open %u
StartupNotify=false
MimeType=x-scheme-handler/puddl;
EOF

xdg-desktop-menu install ~/.local/share/applications/puddl-puddl.desktop

# test run
xdg-open puddl://4c016f98-209d-4476-a6f6-fdd07b2b3d9e/
```

### Firefox
This guy! Thanks! https://superuser.com/a/1351073/182585


### docs
- https://superuser.com/questions/162092/how-can-i-register-a-custom-protocol-with-xdg
- https://unix.stackexchange.com/questions/497146/create-a-custom-url-protocol-handler
- maybe `xdg-mime default puddl.desktop application/prs.puddl`
