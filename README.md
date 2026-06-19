# sketch

My personal thoughts, sketches, journal entries, etc.

## Build

On Linux env, use `uv` to create the project virtual environment for the first
time:

```bash
uv venv
uv pip install -r requirements.txt
```

After that, enter the virtual environment before building or previewing docs:

```bash
source .venv/bin/activate

# build static HTML
make
```

For live preview while editing:

```bash
source .venv/bin/activate
sphinx-autobuild source build/html

# exit venv when finished
deactivate
```

## VSCode

If VSCode or Esbonio marks Sphinx extensions in `source/conf.py` as missing,
make sure the background Sphinx process uses the project virtual environment.

This project keeps `.vscode/` ignored, so add the following local workspace
setting in `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    "esbonio.sphinx.pythonCommand": "${workspaceFolder}/.venv/bin/python"
}
```

Then restart the Esbonio language server or reload the VSCode window.
