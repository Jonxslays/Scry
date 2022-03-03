from __future__ import annotations

from typing import Callable

import nox
import toml

SessionT = Callable[[nox.Session], None]
InjectorT = Callable[[SessionT], SessionT]

with open("pyproject.toml") as f:
    data = toml.loads(f.read())["tool"]["poetry"]
    deps = data["dev-dependencies"]
    deps.update(data["dependencies"])
    DEPS: dict[str, str] = {k.lower(): f"{k}{v}" for k, v in deps.items()}


def install(*packages: str) -> InjectorT:
    def inner(func: SessionT) -> SessionT:
        def wrapper(session: nox.Session) -> None:
            try:
                session.install("-U", *(DEPS[p] for p in packages))
                return func(session)
            except KeyError as e:
                session.error(f"{e} is not in the pyproject.toml")

        wrapper.__name__ = func.__name__
        return wrapper

    return inner


@nox.session(reuse_venv=True)
@install("mypy")
def types_mypy(session: nox.Session) -> None:
    session.run("mypy", "scry")


@nox.session(reuse_venv=True)
@install("pyright")
def types_pyright(session: nox.Session) -> None:
    session.run("pyright")


@nox.session(reuse_venv=True)
@install("black", "len8")
def formatting(session: nox.Session) -> None:
    session.run("black", ".", "--check")
    session.run("len8")


@nox.session(reuse_venv=True)
@install("flake8", "isort")
def imports(session: nox.Session) -> None:
    session.run("isort", "scry", "-cq")
    session.run(
        "flake8",
        "scry",
        "--select",
        "F4",
        "--extend-ignore",
        "E,F",
        "--extend-exclude",
        "__init__.py,",
    )


@nox.session(reuse_venv=True)
def version_check(session: nox.Session) -> None:
    toml_version = None
    init_version = None

    with open("pyproject.toml") as pytoml:
        for line in filter(lambda line: line.startswith("version"), pytoml):
            toml_version = line.split(" = ")[-1].strip('"\n')

    if not toml_version:
        session.error("Couldn't find version info in pyproject.toml.")

    with open("scry/__init__.py") as pyinit:
        for line in filter(lambda line: line.startswith("__version__"), pyinit):
            init_version = line.split(" = ")[-1].strip('"\n')

    if not init_version:
        session.error("Couldn't find version info in __init__.py")

    if toml_version != init_version:
        session.error(f"pyproject v{toml_version} does not match init v{init_version}")
