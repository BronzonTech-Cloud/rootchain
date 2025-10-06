# Contributing to RootChain

Thanks for wanting to contribute! Please follow these steps to make collaboration smooth.

- Fork the repository and create branches for your changes.
- Follow the coding style: use `black` and `isort` for Python.
- Run tests locally with `pytest` before submitting PRs.
- Include unit tests for new features and bug fixes.
- Keep changes small and well-documented.

Run the following locally to set up the development environment:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.lock
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

For major changes, open an issue first to discuss the design.
