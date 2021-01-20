from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class XiaoquItem:
    xiaoqu_id: str
    name: str
    district: str
    area: str
    built_year: Optional[int]
    tags: List[str]

@dataclass
class XiaoQuDailyStats:
    xiaoqu_id: str
    name: str
    for_rent: int
    deal_in_90days: int
