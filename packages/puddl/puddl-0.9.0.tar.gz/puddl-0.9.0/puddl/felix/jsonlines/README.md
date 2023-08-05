# Testing
```
puddl json load test t1 <<'EOF'
{"id": 1, "name": "hello"}
{"id": 2, "name": "world"}
EOF

puddl db shell --app test <<< "SELECT * FROM t1"
```
