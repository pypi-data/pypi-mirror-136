# Actively maintained fork of [asana-cli](https://github.com/AlJohri/asana-cli)

[![PyPI Version](https://img.shields.io/pypi/v/asana-cli.svg)](https://pypi.python.org/pypi/asana-cli)
[![License Status](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/AlJohri/asana-cli/master/LICENSE)

A command line interface for [Asana](app.asana.com/)

Currently supports:
* Listing of:
  + Workspaces
  + Projects for given workspace
  + Sections for given project
  + Tasks for projects (and sections)
* Deleting tasks
* Marking tasks (not) completed
* Moving tasks between projects (and sections)

## Usage

```
$ asana
Usage: asana [OPTIONS] COMMAND [ARGS]...

Examples:
    asana list workspaces
    asana list projects --workspace="Personal Projects"
    asana list tasks --workspace="Personal Projects" --project="Test"
    asana list sections --workspace="Personal Projects" --project="Test"
    asana list tasks --workspace="Personal Projects" --project="Test" --section="Column 1"

    asana delete tasks --workspace="Personal Projects" --project="Test" --section="Column 1"
    asana mark tasks --workspace="Personal Projects" --project="Test" --section="Column 1" --completed
    asana mark tasks --workspace="Personal Projects" --project="Test" --section="Column 1" --not-completed

    asana move tasks --workspace="Personal Projects" --from-project="Test" --from-section="Column 1" --to-section="Column 2"

    Options:
      --help  Show this message and exit.

    Commands:
      delete
      list
      mark
      move
```

## Setup

make build && make install
