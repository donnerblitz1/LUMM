from typing import Optional
from dataclasses import dataclass

@dataclass
class Business:
    name: str
    address: Optional[str]
    phone: Optional[str]
    website: Optional[str]
    email: Optional[str]  # 👈 hier ergänzt
    source: str

