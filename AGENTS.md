# Python environment and build validation

- Use `uv` to manage the project virtual environment at `.venv` in the
  repository root. All documentation builds must use this environment,
  even if the global environment can build successfully.
- If `.venv/bin/python` does not exist, create the environment from the
  repository root:

  ```sh
  uv venv
  ```

- Install the project dependencies when setting up the environment or
  after changing `requirements.txt`:

  ```sh
  uv pip install --python .venv/bin/python -r requirements.txt
  ```

- Validate documentation changes from the repository root using the
  virtual environment's Sphinx executable:

  ```sh
  source .venv/bin/activate
  make html
  git diff --check
  ```

- On Linux (including WSL), `make` requires the project's `.venv` to be
  activated and always uses its Sphinx executable. If it exits with an
  environment setup message, follow those instructions before retrying.

- Keep VS Code's Python interpreter and Esbonio's Sphinx environment
  pointed at `${workspaceFolder}/.venv/bin/python`, matching the existing
  `.vscode/settings.json` configuration. If VS Code retains an old
  interpreter selection, select `.venv/bin/python` and reload the window.
- Reuse an existing working `.venv`; do not recreate it for each build.
  Keep `.venv/` and generated `build/` files out of version control.
