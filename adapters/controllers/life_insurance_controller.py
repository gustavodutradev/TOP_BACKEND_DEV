from flask import jsonify
from core.services.life_insurance_service import LifeInsuranceService
import logging
from http import HTTPStatus


class LifeInsuranceController:

    def __init__(self, app):
        self.life_insurance_service = LifeInsuranceService()
        self.app = app
        self.routes()

    def routes(self) -> None:
        self.app.add_url_rule(
            "/api/v1/life-insurance-data/<account_number>",
            "life_insurance_handler",
            self.get_insurance_for_account,
            methods=["GET"],
        )

    def get_insurance_for_account(self, account_number):
        try:
            insurance_data = self.life_insurance_service.get_life_insurance_data(
                account_number
            )
            logging.info(f"Life Insurance data for {account_number}: {insurance_data}")
            return jsonify(insurance_data)
        except Exception as e:
            logging.error(
                f"Error getting Life Insurance data for account {account_number}: {str(e)}"
            )
            return jsonify({"error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
