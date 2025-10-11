from typing import List, Protocol

from app.core.entities.payroll import Payroll


class IPayrollRepository(Protocol):
    async def create(self, payroll: Payroll) -> Payroll: ...
    async def list_all(self) -> List[Payroll]: ...
