# Context strategy

**Engagement:** generated-source cousin / kubernetes-client-python
**Author:** FDE
**Date:** 2026-08-17
**Status:** draft
**Source revision:** kubernetes-client/python@9c3456a
**Confidence:** scale is confirmed from `git ls-files`; working set is a judgment

## Scale
- **Files:** 7365 · **Band:** 5k–50k
- **Scope:** whole repo, but never read the generated client/docs broadly
- **Approach:** Search and script first. Read only the authored remainder + spec + generate scripts.

## Working set
- `kubernetes/.openapi-generator/FILES` — generator inventory (1,677 paths)
- `scripts/update-client.sh` — how the client is produced
- `scripts/swagger.json` / `kubernetes/swagger.json.unprocessed` — vendored spec
- `kubernetes/__init__.py` — public surface (handwritten)
- `kubernetes/base/config/kube_config.py` — authored config
- `kubernetes/utils/` · `kubernetes/informer/` — authored
- `setup.py` · `requirements.txt`
- `.github/workflows/test.yaml` — PR validation (`tox`)
- `README.md` — says canonical OpenAPI spec is the Kubernetes main repo

## CLAUDE.md
deferred — throwaway clone; findings live in this workspace and VALIDATION.md Run 12

## Next step
`repo-recon` scoped to authored vs generated split; do not map `kubernetes/client/api/*.py` as the system.
