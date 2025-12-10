.PHONY: test demo
test:
\tpython -m pytest -q

demo:
\t./run_local_demo.sh
