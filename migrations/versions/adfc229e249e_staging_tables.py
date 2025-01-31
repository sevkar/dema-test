"""staging tables

Revision ID: adfc229e249e
Revises:
Create Date: 2025-01-31 17:03:26.740399

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = "adfc229e249e"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(text("create schema if not exists raw"))
    op.execute(text("create schema if not exists staging"))
    op.execute(
        text("""
        CREATE TABLE staging.category (
        id     SERIAL PRIMARY KEY,
        name   TEXT NOT NULL UNIQUE
        );
        
        CREATE TABLE staging.subcategory (
            id    SERIAL PRIMARY KEY,
            category_id        INT NOT NULL REFERENCES staging.category(id),
            name  TEXT NOT NULL
        );
        CREATE UNIQUE INDEX idx_subcategory_category_id_name ON staging.subcategory (category_id, name);
        
        CREATE TABLE staging.product (
            product_id TEXT PRIMARY KEY,
            name     TEXT NOT NULL,
            sub_category_id  INT REFERENCES staging.subcategory(id),
            quantity         INT NOT NULL,
            created_at       TIMESTAMP NOT NULL DEFAULT now()
        );
        
        CREATE TABLE staging.channel_group (
            id   SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );
        
        CREATE TABLE staging.channel (
            id         SERIAL PRIMARY KEY,
            name       TEXT NOT NULL UNIQUE,
            channel_group_id   INT REFERENCES staging.channel_group(id)
        );
        
        CREATE TABLE staging.campaign (
            id     SERIAL PRIMARY KEY,
            name   TEXT NOT NULL UNIQUE
        );
        
        CREATE TABLE staging."order" (
            order_id      TEXT PRIMARY KEY,
            currency   TEXT NOT NULL,
            shipping_cost NUMERIC NOT NULL,
            channel_id    INT NOT NULL REFERENCES staging.channel(id),
            campaign_id   INT REFERENCES staging.campaign(id), -- can be null
            created_at    TIMESTAMP NOT NULL DEFAULT now()
        );
        
        CREATE TABLE staging.order_line_item (
            id  SERIAL PRIMARY KEY,
            order_id       TEXT NOT NULL REFERENCES staging."order"(order_id),
            product_id     TEXT NOT NULL REFERENCES staging.product(product_id),
            quantity       INT NOT NULL,
            amount         NUMERIC NOT NULL
        );
    """)
    )


def downgrade() -> None:
    op.execute(text("drop schema if exists staging cascade"))
