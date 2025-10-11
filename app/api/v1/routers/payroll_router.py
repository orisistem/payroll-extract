from fastapi import APIRouter, Depends

from app.application.payroll_service import PayrollService
from app.container import get_payroll_service
from app.core.entities.payroll import Payroll

router = APIRouter(prefix="/payrolls", tags=["Payrolls"])


@router.post("/", response_model=Payroll)
async def create_payroll(
    payroll: Payroll, service: PayrollService = Depends(get_payroll_service)
):
    return await service.register(payroll)


@router.get("/", response_model=list[Payroll])
async def list_payrolls(service: PayrollService = Depends(get_payroll_service)):
    return await service.process_use_case.repository.list_all()
