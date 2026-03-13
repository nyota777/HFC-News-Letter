from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Article:
    title: str
    url: str
    source: str
    pub_date: Optional[datetime] = None
    body: str = ""
    summary: str = ""
    takeaway: str = ""
    category: str = ""
