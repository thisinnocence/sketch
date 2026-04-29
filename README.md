# sketch

My personal thoughts, sketches, journal entries, etc.

## Build (Linux)

This workflow is for Linux shells (for example Ubuntu + zsh/bash).

Build the Sphinx HTML docs with `uv`:

```bash
uv venv
uv pip install -r requirements.txt
uv run make
```

Alternative (activate venv first):

```bash
source .venv/bin/activate
make
```
