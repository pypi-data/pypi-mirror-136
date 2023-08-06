# ingeniictl - Ingenii's Swiss Army Knife

- [ingeniictl - Ingenii's Swiss Army Knife](#ingeniictl---ingeniis-swiss-army-knife)
  - [Overview](#overview)
  - [Development](#development)
    - [Makefiles](#makefiles)
    - [Releasing New Version](#releasing-new-version)
  - [Install](#install)
  - [Environment Variables](#environment-variables)
  - [Executable](#executable)
  - [Commands](#commands)
  - [Options](#options)

## Overview

We have been using Makefiles to help us augument Pulumi with pre/post deployment automation. The goal of this CLI is not to fully replace the Makefiles and the countless targets in there, but to greatly reduce their size.

## Development

1. Launch the Visual Studio Code
2. Open the project in Dev Container
3. Congratulations. You have all necessary tools to extend this CLI.

### Makefiles

There are some handy shortcuts in the makefile.

- `make install` - Installs all dependencies
- `make build` - Builds the ingeniictl and outputs the `whl` and `zip` files in the `dist` dir.
- `make publish TOKEN=<pypi token>` - Builds and publishes the ingeniictl to pypi.
- `make publish-test TOKEN=<pypi token>` - Builds and publishes the ingeniictl to the test pypi.
- `make test` - Runs tests.

### Releasing New Version

1. Make your changes
2. Test locally
3. Bump the package version: `poetry version <patch | minor | major | prepatch | preminor | premajor | rerelease>`
4. Open a Pull Request (Merge to Releases)
5. Get someone to review and merge
6. The CI will automatically publish the new version

## Install

`pip install ingeniictl`

## Environment Variables

`II_LOG_ENABLE_COLORS` - Set to `0` to disable colors in the output messages.  
`II_LOG_ENABLE_DATETIME_PREFIX` - Set to `0` to disable the date/time prefix in the output messages.

## Executable

```
ingeniictl
```

## Commands

[infra](./docs/commands/infra.md) - Infrastructure Toolkit

## Options
```shell
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.
  --help 
```
