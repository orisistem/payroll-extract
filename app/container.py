from app.application.payroll_service import PayrollService
from app.core.use_cases.process_payroll_use_case import ProcessPayrollUseCase
from app.infrastructure.database.payroll_repository import PayrollRepository


def get_payroll_service() -> PayrollService:
    repository = PayrollRepository()
    use_case = ProcessPayrollUseCase(repository)
    return PayrollService(use_case)
