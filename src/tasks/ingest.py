from pathlib import Path

import pandas as pd
from prefect import task, get_run_logger
from pydantic import BaseModel, ValidationError
from sqlalchemy import create_engine

from settings import settings


@task
def load_dataset(path: Path, filename: str) -> pd.DataFrame:
    logger = get_run_logger()
    logger.info(f"Loading dataset from {path / filename}")
    return pd.read_csv(path / filename)


@task
def validate_dataset(
    dataset: pd.DataFrame, schema: type[BaseModel], skip_failed: bool = True
) -> pd.DataFrame:
    """
    Validate a pandas DataFrame against a Pydantic schema.
    """
    logger = get_run_logger()
    logger.info(
        f"Validating dataset with schema {schema.__name__}, skip_failed={skip_failed}"
    )
    valid_data = []
    for idx, row in dataset.iterrows():
        try:
            schema.model_validate(row.to_dict())
            valid_data.append(row)
        except ValidationError as e:
            if not skip_failed:
                logger.warning(f"Validation error: {e}")
                raise e
    logger.info(f"Validated dataset with schema {schema.__name__}")
    return pd.DataFrame(valid_data)


@task
def persist_raw_data(data: pd.DataFrame, table: str, schema: str = "raw") -> None:
    logger = get_run_logger()
    logger.info(f"Persisting data to {schema}.{table}")
    engine = create_engine(settings.DATABASE_DSN)
    data.to_sql(table, engine, schema=schema, if_exists="replace", index=False)
    logger.info(f"Persisted data to {schema}.{table}")
