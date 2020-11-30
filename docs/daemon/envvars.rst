.. currentmodule:: config

Environment Variables
=====================

=====================  ===============================  ================================================
Variable Name          Default Value                    Description
=====================  ===============================  ================================================
`API_TOKEN`            `None`                           Secret api token for server daemon communication
`HOST`                 `"0.0.0.0"`                      Host for http server to listen on
`PORT`                 `8000`                           Port for http server to listen on
`DEBUG`                `False`                          Debug mode
`SQL_SERVER_LOCATION`  `"postgresql://localhost:5432"`  Location of sql server
`SQL_SERVER_DATABASE`  `"cryptic"`                      Database of sql server
`SQL_SERVER_USERNAME`  `"cryptic"`                      Username of sql server
`SQL_SERVER_PASSWORD`  `"cryptic"`                      Password of sql server
`SQL_SHOW_STATEMENTS`  `False`                          Whether sql queries should be logged
`SQL_CREATE_TABLES`    `False`                          Whether to create tables automatically
`SENTRY_DSN`           `None`                           Sentry data source name
=====================  ===============================  ================================================
