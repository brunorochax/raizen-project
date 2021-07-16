# Environment

This environment was built with docker-compose.

## Services

* win-py-runner: Responsible for run python scripts that depends of pywin32.
* postregs: Database for airflow.
* scheduler: Airflow scheduler.
* webserver: Airflow webserver.