from prisma.models import Payroll as PrismaPayroll

from app.core.interfaces.payroll_repository_interface import IPayrollRepository
from app.infrastructure.database.prisma_client import prisma


class PayrollRepository(IPayrollRepository):

    async def create(
        self,
        employee: str,
        position: str,
        gross_value: float,
        net_value: float,
        month_year: str,
    ) -> PrismaPayroll:
        return await prisma.payroll.create(
            data={
                "employee": employee,
                "position": position,
                "gross_value": gross_value,
                "net_value": net_value,
                "month_year": month_year,
            }
        )

    async def list_all(self) -> list[PrismaPayroll]:
        return await prisma.payroll.find_many(order={"createdAt": "desc"})
