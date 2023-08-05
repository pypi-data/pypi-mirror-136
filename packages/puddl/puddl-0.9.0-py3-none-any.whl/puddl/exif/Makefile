.PHONY: default
default: load definitions flask

# put a few pics into memory for faster feedback loops
.PHONY: pics-to-shm
pics-to-shm:
	~/puddl/mount-pictures || true
	mkdir -p /dev/shm/pics
	cp ~/puddl/pictures/202109* /dev/shm/pics/

.PHONY: definitions
definitions:
	puddl-db shell exif < definitions.sql

.PHONY: load
load:
	./load.py /dev/shm/pics

.PHONY: flask
flask:
	export FLASK_APP=puddl.exif.app
	export FLASK_DEBUG=1
	flask run

.PHONY: show
show:
	firefox index.html
