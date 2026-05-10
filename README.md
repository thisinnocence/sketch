# sketch

My personal thoughts, sketches, journal entries, etc.

## Build

On Linux env, build the Sphinx HTML docs with `uv`:

```bash
uv venv
uv pip install -r requirements.txt
uv run make
```

Or you can:

```bash
# activate venv
source .venv/bin/activate
make

# deactivate venv
deactivate
```

