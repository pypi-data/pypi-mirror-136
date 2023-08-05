.PHONY: default
default: code-style test

.PHONY: DANGER_remove_everything
DANGER_remove_everything:
	./env/dev/DANGER_destroy_compose_environment.sh
	rm .env

.PHONY: code-style
code-style:
	./env/dev/git-hooks/pre-commit

.PHONY: test
test:
	puddl-db health
	pytest puddl/tests/
	puddl-db health >/dev/null
	puddl-db ls >/dev/null
	puddl-config show >/dev/null

.PHONY: e2e-setup-py
e2e-setup-py:
	./env/dev/bin/e2e-setup-py.sh

.PHONY: build
build:
	python setup.py sdist bdist_wheel

.PHONY: release-test-pypi
release-test-pypi: clean code-style test build
	twine upload --repository testpypi dist/*

.PHONY: release-pypi
release-pypi:
	twine upload --repository pypi dist/*

.PHONY: release
release: clean test build release-pypi

.PHONY: e2e-pypi
e2e-pypi:
	./env/dev/bin/e2e-pypi.sh

.PHONY: clean
clean:
	rm -rf build/ dist/

.PHONY: db_reload
db_reload:
	docker-compose exec -u postgres db pg_ctl reload

.PHONY: db_logs
db_logs:
	docker-compose logs --tail=50 -f db
