from prefect import task, get_run_logger
from sqlalchemy import text, create_engine

from settings import settings


@task
def update_categories() -> None:
    """
    Extract categories and subcategories from the inventory DataFrame and insert them into the staging schema.
    """
    logger = get_run_logger()
    logger.info("Updating categories and subcategories")
    engine = create_engine(settings.DATABASE_DSN)
    with engine.connect() as conn:
        categories_stmt = text(
            'SELECT DISTINCT category, "subCategory" FROM raw.inventory'
        )
        result = conn.execute(categories_stmt).fetchall()

    category_stmt = text(
        "INSERT INTO staging.category (name) VALUES (:name) ON CONFLICT DO NOTHING;"
    )
    category_values = [{"name": row[0]} for row in result]

    subcategory_stmt = text(
        "INSERT INTO staging.subcategory (category_id, name) "
        "VALUES ((SELECT id FROM staging.category WHERE name = :category), :name) "
        "ON CONFLICT DO NOTHING;"
    )
    subcategory_values = [{"category": row[0], "name": row[1]} for row in result]

    engine = create_engine(settings.DATABASE_DSN)
    with engine.connect() as conn:
        conn.execute(category_stmt, category_values)
        conn.execute(subcategory_stmt, subcategory_values)
        conn.commit()

    logger.info("Categories and subcategories updated")


@task
def update_channels() -> None:
    """
    Extract channels and channel groups from the orders DataFrame and insert them into the staging schema.
    """
    logger = get_run_logger()
    logger.info("Updating channels and channel groups")
    engine = create_engine(settings.DATABASE_DSN)
    with engine.connect() as conn:
        channels_stmt = text('SELECT DISTINCT "channelGroup", channel FROM raw.orders')
        result = conn.execute(channels_stmt).fetchall()

    channel_group_stmt = text(
        "INSERT INTO staging.channel_group (name) VALUES (:name) ON CONFLICT DO NOTHING;"
    )
    channel_group_values = [{"name": row[0]} for row in result]

    channel_stmt = text(
        "INSERT INTO staging.channel (channel_group_id, name) "
        "VALUES ((SELECT id FROM staging.channel_group WHERE name = :group), :name) "
        "ON CONFLICT DO NOTHING;"
    )
    channel_values = [{"group": row[0], "name": row[1]} for row in result]

    with engine.connect() as conn:
        conn.execute(channel_group_stmt, channel_group_values)
        conn.execute(channel_stmt, channel_values)
        conn.commit()

    logger.info("Channels and channel groups updated")


@task
def update_campaigns() -> None:
    """
    Extract campaigns from the orders DataFrame and insert them into the staging schema.
    """
    logger = get_run_logger()
    logger.info("Updating campaigns")
    engine = create_engine(settings.DATABASE_DSN)
    with engine.connect() as conn:
        campaigns_stmt = text("SELECT DISTINCT campaign FROM raw.orders")
        campaigns = conn.execute(campaigns_stmt).scalars().all()

    campaign_stmt = text(
        "INSERT INTO staging.campaign (name) VALUES (:name) ON CONFLICT DO NOTHING;"
    )
    campaign_values = [
        {"name": campaign} for campaign in campaigns if campaign is not None
    ]

    with engine.connect() as conn:
        conn.execute(campaign_stmt, campaign_values)
        conn.commit()

    logger.info("Campaigns updated")


@task
def update_products() -> None:
    """
    Extract products from the inventory DataFrame and insert them into the staging schema.
    """
    logger = get_run_logger()
    logger.info("Updating products")
    engine = create_engine(settings.DATABASE_DSN)
    with engine.connect() as conn:
        products_stmt = text(
            'SELECT DISTINCT "productId", name, quantity, "subCategory" FROM raw.inventory'
        )
        result = conn.execute(products_stmt).fetchall()

    product_stmt = text(
        "INSERT INTO staging.product (product_id, name, sub_category_id, quantity) "
        "VALUES (:product_id, :name, (SELECT id FROM staging.subcategory WHERE name = :sub_category), :quantity) "
        "ON CONFLICT DO NOTHING;"
    )
    product_values = [
        {
            "product_id": row[0],
            "name": row[1],
            "quantity": row[2],
            "sub_category": row[3],
        }
        for row in result
    ]

    with engine.connect() as conn:
        conn.execute(product_stmt, product_values)
        conn.commit()

    logger.info("Products updated")


@task
def transform_orders() -> None:
    """
    Extract orders from the orders DataFrame and insert them into the staging schema.
    """
    logger = get_run_logger()
    logger.info("Transforming orders")
    engine = create_engine(settings.DATABASE_DSN)
    with engine.connect() as conn:
        orders_stmt = text(
            'SELECT "orderId", "dateTime", currency, "shippingCost", channel, campaign '
            "FROM raw.orders"
        )
        result = conn.execute(orders_stmt).fetchall()

    order_stmt = text(
        "INSERT INTO staging.order (order_id, created_at, currency, shipping_cost, channel_id, campaign_id) "
        "VALUES (:order_id, :created_at, :currency, :shipping_cost, "
        "(SELECT id FROM staging.channel WHERE name = :channel), "
        "(SELECT id FROM staging.campaign WHERE name = :campaign)) "
        "ON CONFLICT DO NOTHING;"
    )
    order_values = [
        {
            "order_id": row[0],
            "created_at": row[1],
            "currency": row[2],
            "shipping_cost": row[3],
            "channel": row[4],
            "campaign": row[5],
        }
        for row in result
    ]

    with engine.connect() as conn:
        conn.execute(order_stmt, order_values)
        conn.commit()

    logger.info("Orders transformed")
