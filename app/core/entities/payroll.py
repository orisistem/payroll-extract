from datetime import datetime

from pydantic import BaseModel


class Payroll(BaseModel):
    id: str | None = None
    employee: str
    position: str
    gross_value: float
    net_value: float
    month_year: str
    createdAt: datetime | None = None
