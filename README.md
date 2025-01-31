# Data Ingestion Pipeline for Dema

A Prefect pipeline that ingests data from two CSV sources, persists the raw data to a database, 
and then transforms the data into a normalized form.

## Overview

This pipeline created using tools:
- [Prefect](https://www.prefect.io) for workflow management
- [Pandas](https://pandas.pydata.org) for data manipulation
- [SQLAlchemy](https://www.sqlalchemy.org) for database interaction
- [Pydantic](https://pydantic.dev) for data validation
- **Postgres** as a database

## Installation

```bash
make init
```

## Usage

To run the pipeline:

```bash
make local_run
```
It will run database in Docker and Prefect flow in the local environment.

## Development

Copy `.env.example` to `.env` and fill in the required environment variables.

Update `DATABASE_DSN` in the `.env` file with your database connection string.

## Next Steps and TODOs

- Run Prefect server and flows in Docker container
- Add unittests for the pipeline tasks
- Add integration tests for the pipeline
- Optimize the pipeline for large datasets 
__(current implementation works for relatively small datasets, work with raw data should be done in chunks)__