from app.core.entities.payroll import Payroll
from app.core.use_cases.process_payroll_use_case import ProcessPayrollUseCase


class PayrollService:

    def __init__(self, process_use_case: ProcessPayrollUseCase):
        self.process_use_case = process_use_case

    async def register(self, payroll: Payroll):
        return await self.process_use_case.execute(payroll)
