from app.core.entities.payroll import Payroll
from app.core.interfaces.payroll_repository_interface import IPayrollRepository


class ProcessPayrollUseCase:

    def __init__(self, repository: IPayrollRepository):
        self.repository = repository

    async def execute(self, payroll: Payroll) -> Payroll:
        return await self.repository.create(payroll)
