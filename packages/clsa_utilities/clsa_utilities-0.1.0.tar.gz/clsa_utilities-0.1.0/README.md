# `pypi-name-squatter`

This repository contains the minimal amount of code to build a Python package,
whose purpose is to be uploaded onto [PyPI](https://pypi.org/) in the name of
[name squatting](https://github.com/pypa/warehouse/issues/4004). The purpose of
this is to prevent
[dependency confusion](https://medium.com/@alex.birsan/dependency-confusion-4a5d60fec610)
attacks.

## Steps

1. Modify the package name in `pyproject.toml` from `clsa_test` to the new
   project name.

1. Modify the directory named `clsa_test` to the new project name.

1. Publish to [PyPI](https://pypi.org/):

   ```bash
   FLIT_USERNAME=derekwanclsa FLIT_PASSWORD='Frisk carport corpsman' flit publish
   ```

## Registered packages:

| Date       | Package                                            |
| ---------- | -------------------------------------------------- |
| 2022-01-26 | [`clsa_test`](https://pypi.org/project/clsa_test/) |
| 2022-01-26 | [`clsa_pypi`](https://pypi.org/project/clsa_pypi/) |
