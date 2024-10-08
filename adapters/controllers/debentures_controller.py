from flask import jsonify
from core.services.debentures_service import DebenturesService


class DebenturesController:
    def __init__(self) -> None:
        self.debentures_service = DebenturesService()

    def get_anbima_debentures(self, date):
        anbima_debentures = self.debentures_service.get_anbima_debentures(date)
        return jsonify(anbima_debentures)
