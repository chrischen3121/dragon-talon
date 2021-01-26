from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class XiaoquInfo:
    item_name = "xiaoqu_info"
    xiaoqu_id: str
    name: str
    district: str
    area: str
    built_year: Optional[int]
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
