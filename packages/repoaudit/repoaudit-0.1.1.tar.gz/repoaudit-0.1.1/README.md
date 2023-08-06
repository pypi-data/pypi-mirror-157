# repoaudit

A tool for validating apt and yum repositories.

## Installation and Usage

To install repoaudit from PyPI:

```
pip install repoaudit
```

Then run:

```
repoaudit --help
```

## Examples

```
# validate all distros of azure-cli apt repo
repoaudit apt https://packages.microsoft.com/repos/azure-cli/

# validate only focal and bionic distros of azure-cli apt repo
repoaudit apt --dist focal --dist bionic https://packages.microsoft.com/repos/azure-cli/

# validate azurecore repo
repoaudit yum https://packages.microsoft.com/yumrepos/azurecore/

# validate all nested yumrepos
repoaudit yum -r https://packages.microsoft.com/yumrepos/
```

## Development


First install poetry:

https://python-poetry.org/docs/#installation

Then clone the repo and cd into the repoaudit directory.

Run `poetry install` to install repoaudit's dependencies.

To load the poetry shell and run repoaudit:

```
poetry shell
repoaudit
```

Altenatively you can run:

```
poetry run repoaudit
```

## Releasing

```
poetry publish --build
```
