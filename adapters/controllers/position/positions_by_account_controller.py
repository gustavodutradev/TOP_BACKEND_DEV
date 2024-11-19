from flask import jsonify
from core.services.position.positions_by_account_service import (
    PositionsByAccountService,
)
import logging
from http import HTTPStatus


class PositionsByAccountController:

    def __init__(self, app):
        self.positions_by_account_service = PositionsByAccountService()
        self.app = app
        self.routes()

    def routes(self) -> None:
        self.app.add_url_rule(
            "/api/v1/positions/positions-by-account/<account_number>",
            "positions_by_account_handler",
            self.get_positions_for_account,
            methods=["GET"],
        )

    def get_positions_for_account(self, account_number):
        try:
            positions_data = self.positions_by_account_service.get_positions_by_account(
                account_number
            )
            logging.info(f"Positions data for {account_number}: {positions_data}")
            return jsonify(positions_data)
        except Exception as e:
            logging.error(
                f"Error getting Positions data for account {account_number}: {str(e)}"
            )
            return jsonify({"error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
