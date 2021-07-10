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
pipenv sync --dev
pipenv run docs
```
Note that you need to have [Docker](https://www.docker.com/) installed for this!


## Development

### Prerequisites
- [Python](https://python.org/) >=3.9
- [Pipenv](https://github.com/pypa/pipenv/)
- [Black](https://github.com/psf/black/)
- [Git](https://git-scm.com/)
- [Docker](https://www.docker.com/) and [docker-compose](https://docs.docker.com/compose/) (recommended)
- [PyCharm Community/Professional](https://www.jetbrains.com/pycharm/) (recommended)
- [An instance of the Cryptic Java Server](https://github.com/cryptic-game/java-backend) (recommended)


### Clone the repository

#### SSH (recommended)
```
git clone git@github.com:cryptic-game/python-daemon.git
```

#### HTTPS
```
git clone https://github.com/cryptic-game/python-daemon.git
```


### Setup Dependencies
Once you have cloned the repository, you need to create a virtual environment and install the dependencies using the following command:
```
pipenv sync --dev
```


### Environment Variables
To set the required environment variables it is necessary to create a file named (exactly) [`.env`](https://pipenv.pypa.io/en/latest/advanced/#automatic-loading-of-env) in the root directory (there is a template for this file in [`daemon.env`](daemon.env)).

|    Variable Name    |                         Description                         |    Default Value     |
|:--------------------|:------------------------------------------------------------|:---------------------|
| LOG_LEVEL           | one of `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`      | `INFO`               |
|                     |                                                             |                      |
| HOST                | Host for the uvicorn server to listen on                    | `0.0.0.0`            |
| PORT                | Port for the uvicorn server to listen on                    | `8000`               |
| RELOAD              | Enable uvicorn auto-reload (for development purposes only!) | `False`              |
| DEBUG               | Enable debug mode                                           | `False`              |
|                     |                                                             |                      |
| API_TOKEN           | Secret api token for server-daemon communication            |                      |
|                     |                                                             |                      |
| SQL_DRIVER          | Name of the SQL connection driver                           | `postgresql+asyncpg` |
| SQL_HOST            | Hostname of the database server                             | `localhost`          |
| SQL_PORT            | Port on which the database server is running                | `5432`               |
| SQL_DATABASE        | Name of the database you want to use                        | `cryptic`            |
| SQL_USERNAME        | Username for the database account                           | `cryptic`            |
| SQL_PASSWORD        | Password for the database account                           | `cryptic`            |
| POOL_RECYCLE        | Number of seconds between db connection recycling           | `300`                |
| POOL_SIZE           | Size of the connection pool                                 | `20`                 |
| MAX_OVERFLOW        | The maximum overflow size of the connection pool            | `20`                 |
| SQL_SHOW_STATEMENTS | whether SQL queries should be logged                        | `False`              |
| SQL_CREATE_TABLES   | whether to create database tables on startup                | `False`              |
|                     |                                                             |                      |
| REDIS_HOST          | Hostname of the redis server                                | `redis`              |
| REDIS_PORT          | Port on which the redis server is running                   | `6379`               |
| REDIS_DB            | Index of the redis database you want to use                 | `0`                  |
|                     |                                                             |                      |
| SENTRY_DSN          | [Optional] Sentry DSN for logging                           |                      |


### Project structure

```
Project
├── daemon
│  ├── endpoints
│  │  ├── __init__.py
│  │  └── <endpoint collection>.py
│  ├── exceptions
│  │  ├── api_exception.py
│  │  └── <endpoint collection>.py
│  ├── models
│  │  └── <endpoint collection>.py
│  └── schemas
│     ├── <endpoint collection>.py
│     ├── daemon.py
│     └── ok.py
└── tests
   ├── endpoints
   │  ├── __init__.py
   │  └── test_<endpoint collection>.py
   └── test_<...>.py
```


### PyCharm configuration

- Open PyCharm and go to `Settings` ➔ `Project: python-daemon` ➔ `Python Interpreter`
- Open the menu `Python Interpreter` and click on `Show All...`
- Click on the plus symbol
- Click on `Pipenv Environment`
- Select `Python 3.9` as `Base interpreter`
- Confirm with `OK`
- Change the working directory to root path  ➔ `Edit Configurations`  ➔ `Working directory`


### Running
To run the Python Daemon yourself, use the `daemon` script:
```
pipenv run daemon
```


### Code Style
Before committing your changes, please check that all unit tests are passing, reformat your code using [black](https://github.com/psf/black) and run the linter:
```
pipenv run test
pipenv run black
pipenv run flake8
```
