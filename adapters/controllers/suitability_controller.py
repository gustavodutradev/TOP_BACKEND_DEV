from flask import jsonify
from core.services.suitability_service import SuitabilityService
import logging
from http import HTTPStatus


class SuitabilityController:

    def __init__(self, app):
        self.suitability_service = SuitabilityService()
        self.app = app
        self.register_routes()

    def register_routes(self) -> None:
        self.app.add_url_rule(
            "/api/v1/get-suitability/<account_number>",
            "get_suitability_handler",
            self.get_suitability,
            methods=["GET"]
        )

    def get_suitability(self, account_number):
        try:
            suitability = self.suitability_service.get_suitability(account_number)
            logging.info(f"Suitability for account {account_number}: {suitability}")
            return jsonify(suitability)
        except Exception as e:
            logging.error(f"Error getting suitability for account {account_number}: {str(e)}")
            return jsonify({"error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
