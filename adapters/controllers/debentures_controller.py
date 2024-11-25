from flask import jsonify, request
from core.services.debentures_service import AnbimaDebenturesService
from database.connection import (
    get_db,
)  # Assumindo que você tenha um método para obter a sessão do DB
import logging


class AnbimaDebenturesController:
    def __init__(self, app):
        self.anbima_debentures_service = AnbimaDebenturesService()
        self.app = app
        self.routes()

    def routes(self) -> None:
        self.app.add_url_rule(
            "/api/v1/get-anbima-debentures/<date>",
            "anbima_debentures",
            self.get_anbima_debentures,
            methods=["GET"],
        )

    def get_anbima_debentures(self, date):
        try:
            db = next(get_db())
            result = self.anbima_debentures_service.get_anbima_debentures(db, date)

            if isinstance(result, dict) and "error" in result:
                logging.error(f"Erro retornado pelo serviço: {result['error']}")
                return jsonify(result), 500

            return (
                jsonify({"message": "Dados salvos com sucesso!", "result": result}),
                200,
            )
        except Exception as e:
            logging.error(f"Erro ao buscar dados da Anbima: {e}")
            return jsonify({"error": str(e)}), 500
