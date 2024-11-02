from core.services.management_reports.monthly_tir_service import MonthlyTIRReportService
from adapters.controllers.management_reports.abstract_report_controller import (
    AbstractReportController,
)


class MonthlyTIRController(AbstractReportController):
    def __init__(self, app):
        super().__init__(
            app=app, endpoint="rg_tir_handler", route="/api/v1/rg-monthly-tir"
        )
        self._service = MonthlyTIRReportService()

    @property
    def report_name(self) -> str:
        return "TIR mensal"

    def get_report_service(self):
        return self._service
