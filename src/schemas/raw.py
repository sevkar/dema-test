from datetime import datetime

from pydantic import BaseModel, ConfigDict, NonNegativeInt, NonNegativeFloat
from pydantic.alias_generators import to_camel


class RawBaseModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)


class RawProduct(RawBaseModel):
    product_id: str
    name: str
    quantity: NonNegativeInt
    category: str
    sub_category: str


class RawOrder(RawBaseModel):
    order_id: str
    product_id: str
    currency: str
    quantity: NonNegativeInt
    shipping_cost: NonNegativeFloat
    amount: NonNegativeFloat
    channel: str
    channel_group: str
    campaign: str | None = None
    date_time: datetime
