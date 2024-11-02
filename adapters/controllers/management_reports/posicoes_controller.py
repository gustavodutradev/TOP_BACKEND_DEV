from core.services.management_reports.positions_service import PositionReportService
from adapters.controllers.management_reports.abstract_report_controller import (
    AbstractReportController,
)


class PositionReportController(AbstractReportController):
    def __init__(self, app):
        super().__init__(
            app=app, endpoint="rg_posicoes_handler", route="/api/v1/rg-posicoes"
        )
        self._service = PositionReportService()

    @property
    def report_name(self) -> str:
        return "Posições"

    def get_report_service(self):
        return self._service
