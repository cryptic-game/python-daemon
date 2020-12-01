<h1 align="center">Python Daemon</h1>

<p align="center">
    <img alt="Docker Build" src="https://github.com/cryptic-game/python-daemon/workflows/Docker%20Build/badge.svg">
    <img alt="Flake8" src="https://github.com/cryptic-game/python-daemon/workflows/Flake8/badge.svg">
    <img alt="Sphinx Documentation" src="https://github.com/cryptic-game/python-daemon/workflows/Sphinx%20Documentation/badge.svg">
    <a href="https://deepsource.io/gh/cryptic-game/python-daemon/?ref=repository-badge" style="text-decoration:none">
        <img alt="DeepSource" src="https://deepsource.io/gh/cryptic-game/python-daemon.svg/?label=active+issues&show_trend=true">
    </a>
    <br>
    <a href="https://github.com/psf/black" style="text-decoration:none">
        <img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg">
    </a>
    <a href="https://hub.docker.com/r/crypticcp/python-daemon" style="text-decoration:none">
        <img alt="DockerHub - Python Daemon" src="https://img.shields.io/docker/pulls/crypticcp/python-daemon?style=flat-square&label=DockerHub%20-%20Python%20Daemon">
    </a>
</p>

<p align="center">The official Python Daemon of Cryptic</p>


## Documentation
The documentation can be found on [GitHub Pages](https://cryptic-game.github.io/python-daemon/).

If you want to build the documentation yourself, use the `docs` script:
```
pipenv run docs
```


## Development

### Prerequisites
- [Python](https://python.org/) >=3.8
- [Pipenv](https://github.com/pypa/pipenv/)
- [Black](https://github.com/psf/black/)
- [Git](https://git-scm.com/)
- [Docker](https://www.docker.com/) (recommended)
- [PyCharm Community/Professional](https://www.jetbrains.com/pycharm/) (recommended)
- [An instance of the Cryptic Java Server](https://github.com/cryptic-game/java-backend-dev)

### Setup Dependencies
Once you have cloned the repository, you need to create a virtual environment and install the dependencies using the following command:
```
pipenv sync --dev
```

### Environment Variables
Create a file named (exactly) [`.env`](https://pipenv.pypa.io/en/latest/advanced/#automatic-loading-of-env) in the root directory of this repository with this content:
```
# API_TOKEN=
DEBUG=1
HOST=127.0.0.1
SQL_SERVER_LOCATION=postgresql://172.17.0.1:5432
SQL_SERVER_DATABASE=cryptic
SQL_SERVER_USERNAME=cryptic
SQL_SERVER_PASSWORD=cryptic
SQL_SHOW_STATEMENTS=1
SQL_CREATE_TABLES=1
# SENTRY_DSN=
```
You will need to adjust these environment variables according to the [documentation](https://cryptic-game.github.io/python-daemon/daemon/envvars.html).

### Running
To run the Python Daemon yourself, use the `daemon` script:
```
pipenv run daemon
```

### Code Style
Before committing your changes, please reformat your code using [black](https://github.com/psf/black):
```
black -l 120 .
```
