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

Project-level VSCode settings are tracked in `.vscode/settings.json`. They
point Python and Esbonio at the repository virtual environment, configure
Markdown/RST editing, and keep the documentation workflow consistent across
machines. Recommended extensions are listed in `.vscode/extensions.json`.

Then restart the Esbonio language server or reload the VSCode window.
