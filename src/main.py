from pathlib import Path

from prefect import flow

from schemas.raw import RawProduct, RawOrder
from settings import settings
from tasks.ingest import load_dataset, validate_dataset, persist_raw_data
from tasks.transform import (
    update_categories,
    update_channels,
    update_campaigns,
    update_products,
    transform_orders,
)


@flow(name="dema-pipeline")
def pipeline() -> None:
    # load datasets
    raw_data_dir = Path(Path.cwd() / settings.RAW_DATA_PATH)
    inventory = load_dataset(path=raw_data_dir, filename="inventory.csv")
    orders = load_dataset(path=raw_data_dir, filename="orders.csv")

    # validate datasets
    validated_inventory = validate_dataset(dataset=inventory, schema=RawProduct)
    validated_orders = validate_dataset(dataset=orders, schema=RawOrder)

    # persist raw data
    inventory_result = persist_raw_data.submit(
        data=validated_inventory, table="inventory"
    )
    orders_result = persist_raw_data.submit(data=validated_orders, table="orders")

    # update lookup tables
    categories_result = update_categories.submit(wait_for=[inventory_result])
    updates = [
        update_products.submit(
            wait_for=[inventory_result, categories_result]
        ),  # products depend on categories
        update_channels.submit(wait_for=[orders_result]),
        update_campaigns.submit(wait_for=[orders_result]),
    ]

    transform_orders(wait_for=updates)


pipeline()
