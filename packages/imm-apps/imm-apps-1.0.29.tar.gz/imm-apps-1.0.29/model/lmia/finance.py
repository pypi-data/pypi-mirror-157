from pydantic import BaseModel
from typing import List


class Finance(BaseModel):
    year: int
    total_asset: float
    net_asset: float
    revenue: float
    net_income: float
    retained_earning: float


class Finances:
    def __init__(self, finances: List[Finance]) -> None:
        self.finances = finances

    @property
    def last_income(self):
        if len(self.finances) > 0:
            return self.finances[0].revenue
