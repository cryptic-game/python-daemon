<p>

  [![CI](https://github.com/cryptic-game/python-daemon/actions/workflows/ci.yml/badge.svg)](https://github.com/cryptic-game/python-daemon/actions/workflows/ci.yml)
  [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
  [![Maintainability](https://api.codeclimate.com/v1/badges/fdda287e37d056ac5f0a/maintainability)](https://codeclimate.com/github/cryptic-game/python-daemon/maintainability)
  [![Test Coverage](https://api.codeclimate.com/v1/badges/fdda287e37d056ac5f0a/test_coverage)](https://codeclimate.com/github/cryptic-game/python-daemon/test_coverage)
  [![DockerHub - Python Daemon](https://img.shields.io/docker/pulls/crypticcp/python-daemon?style=flat-square&label=DockerHub%20-%20Python%20Daemon)](https://hub.docker.com/r/crypticcp/python-daemon)

</p>

# Python Daemon

The official Python Daemon of Cryptic


## Documentation
The documentation can be found on [GitHub Pages](https://cryptic-game.github.io/python-daemon/).

If you want to build the documentation yourself, use the `docs` script:
```
pipenv run docs
```


## Development

### Prerequisites
- [Python](https://python.org/) >=3.9
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
