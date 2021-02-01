from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Union


@dataclass
class XiaoquInfo:
    item_name = "xiaoqu_info"
    xiaoqu_id: str
    name: str
    district: str
    area: str
    built_year: Optional[int]
    num_of_buildings: int
    num_of_units: int
    building_type: str
    prop_developer: str
    prop_manager: str
    management_fee: str
    north_latitude: Optional[float]
    east_latitude: Optional[float]
    tags: List[str]


@dataclass
class XiaoquDailyStats:
    item_name = "xiaoqu_daily_stats"

    date: datetime
    xiaoqu_id: str
    name: str
    for_rent: int
    on_sale_count: int
    deal_in_90days: int
    ask_avg_price: int


@dataclass
class Transaction:
    item_name = "transaction"

    house_id: int
    date_: datetime
    towards: str
    decoration: str
    room_type: str
    total_area: float
    floor_location: str
    building_type: str
    delt_avg_price: int
    delt_total_w: int
    ask_total_w: int
    ask_duration_days: int
    xiaoqu_id: str
    xiaoqu_name: str


@dataclass
class ForSale:
    item_name = "for_sale"

    house_id: int
    date_: datetime
    description: str
    room_type: str
    total_area: float
    towards: str
    decoration: str
    floor_location: str
    building_type: str
    five_years_status: int
    ask_total_w: int
    ask_avg_price: int
    ask_duration_days: int
    num_of_followers: int
    xiaoqu_id: str
    xiaoqu_name: str
