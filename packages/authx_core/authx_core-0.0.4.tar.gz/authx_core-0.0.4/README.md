# authx-core 💫

![authx](https://user-images.githubusercontent.com/52716203/136962014-280d82b0-0640-4ee5-9a11-b451b338f6d8.png)

[![codecov](https://codecov.io/gh/yezz123/authx-core/branch/main/graph/badge.svg?token=VPIFTYFNUO)](https://codecov.io/gh/yezz123/authx-core)
[![Pypi](https://img.shields.io/pypi/pyversions/authx_core.svg?color=%2334D058)](https://pypi.org/project/authx_core)
[![framework](https://img.shields.io/badge/Framework-FastAPI-blue?style)](https://fastapi.tiangolo.com/)

## Features

Utilities to help reduce boilerplate and reuse common functionality, Based to
Support Building of [Authx](https://authx.yezz.me) &amp; Authx-lite ⚡:

- **SQLAlchemy Sessions**: The `AuthxDB` class provides an easily-customized
  SQLAlchemy Session dependency.
- **Middleware**: Log basic timing information for every request
- **Inferring Router**: Let FastAPI infer the `response_model` to use based on
  your return type annotation.
- **OpenAPI Simplification**: Simplify your OpenAPI Operation IDs for cleaner
  output from OpenAPI Generator
- **Views**: Stop repeating the same dependencies over and over in the signature
  of related endpoints.

It also adds a variety of more basic utilities that are useful across a wide
variety of projects:

- **GUID Type**: The provided GUID type makes it easy to use UUIDs as the
  primary keys for your database tables

## Requirements

This package is intended for use with any recent version of FastAPI (depending
on `pydantic` and `FastAPI` and `SQLAlchemy`), and Python 3.8+.

## Installation

```bash
pip install authx_core
```

## License

This project is licensed under the terms of the MIT license.
