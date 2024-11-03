from flask import jsonify
from core.services.registration_data_service import RegistrationDataService
import logging
from http import HTTPStatus


class RegistrationDataController:
    def __init__(self, app):
        self.registration_data_service = RegistrationDataService()
        self.app = app
        self.routes()

    def routes(self) -> None:
        self.app.add_url_rule(
            "/api/v1/get-registration-data/<account_number>",
            "get_registration_data_handler",
            self.get_registration_data,
            methods=["GET"],
        )

        self.app.add_url_rule(
            "/api/v1/get-holder-name/<account_number>",
            "get_holder_name_handler",
            self.get_holder_name,
            methods=["GET"],
        )

    def get_registration_data(self, account_number):
        """Retorna todos os dados da conta."""

        try:
            registration_data = self.registration_data_service.get_registration_data(
                account_number
            )
            return jsonify(registration_data)
        except Exception as e:
            logging.error(f"Error processing request: {str(e)}")
            return jsonify({"error": str(e)}), HTTPStatus.HTTP_INTERNAL_ERROR

    def get_holder_name(self, account_number):
        """Retorna apenas o nome do titular da conta."""

        try:
            holder_name = self.registration_data_service.get_holder_name(account_number)
            return jsonify({"holder_name": holder_name})
        except Exception as e:
            logging.error(f"Error processing request: {str(e)}")
            return jsonify({"error": str(e)}), HTTPStatus.HTTP_INTERNAL_ERROR
