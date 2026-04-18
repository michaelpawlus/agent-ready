install:
    .venv/bin/pip install -e .[dev]

test:
    .venv/bin/pytest

score *ARGS:
    .venv/bin/agent-ready score {{ARGS}}
