from flask import jsonify
from core.services.position.positions_by_partner_service import (
    PositionsByPartnerService,
)
import logging
from http import HTTPStatus


class PositionsByPartnerController:

    def __init__(self, app):
        self.positions_by_partner_service = PositionsByPartnerService()
        self.app = app
        self.routes()

    def routes(self) -> None:
        self.app.add_url_rule(
            "/api/v1/positions/positions-by-partner",
            "positions_by_partner_handler",
            self.get_positions_by_partner,
            methods=["GET"],
        )

    def get_positions_by_partner(self):
        try:
            positions_data = (
                self.positions_by_partner_service.get_positions_by_account()
            )
            logging.info(f"Positions data: {positions_data}")
            return jsonify(positions_data)
        except Exception as e:
            logging.error(f"Error getting Positions data: {str(e)}")
            return jsonify({"error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
