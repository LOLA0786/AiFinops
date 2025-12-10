.PHONY: test fmt build push

test:
\tpython -m pytest -q

build-agent:
\tdocker build -f docker/gpu_agent.Dockerfile -t aifinops/gpu-agent:local .

push-agent:
\techo "docker push steps..."

bootstrap:
\t./scripts/bootstrap_megamoats.sh
