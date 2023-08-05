# Configuring Twine
```
cat <<'EOF' > ~/.pypirc
[distutils]
index-servers=
    pypi
    testpypi

[pypi]
username: __token__
password: pypi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

[testpypi]
repository: https://test.pypi.org/legacy/
username: __token__
password: pypi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
EOF
```

# How to Release a New Version
Assuming it is a patch release, first write/check the change log:
```
vi CHANGELOG.md
```

Bump the version
```
bumpversion patch
```

build and push to https://test.pypi.org/project/puddl/
```
make release-test-pypi
```
