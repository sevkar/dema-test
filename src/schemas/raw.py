from datetime import datetime

from pydantic import BaseModel, ConfigDict, PositiveInt, PositiveFloat
from pydantic.alias_generators import to_camel


class RawBaseModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)


class RawProduct(RawBaseModel):
    product_id: str
    name: str
    quantity: PositiveInt
    category: str
    sub_category: str


class RawOrder(RawBaseModel):
    order_id: str
    product_id: str
    currency: str
    quantity: PositiveInt
    shipping_cost: PositiveFloat
    amount: PositiveFloat
    channel: str
    channel_group: str
    campaign: str | None = None
    date_time: datetime
