from flask import jsonify, request
from core.services.debentures_service import AnbimaDebenturesService
from database.connection import get_db  # Assumindo que você tenha um método para obter a sessão do DB
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
            anbima_debentures = self.anbima_debentures_service.get_anbima_debentures(db, date)
            return jsonify(anbima_debentures)
        except Exception as e:
            logging.error(f"Erro ao buscar dados da Anbima: {e}")
            return jsonify({"error": "Ocorreu um erro ao buscar dados da Anbima."}), 500





        # # Obtém os dados da requisição JSON
        # data = request.get_json()
        # reference_date = data.get("referenceDate")

        # if not reference_date:
        #     return jsonify({"error": "Data de referência não fornecida."}), 400

        # # Obtém a sessão do banco de dados
        # db = next(get_db())

        # try:
        #     # Chama o serviço que retorna e persiste os dados
        #     anbima_debentures = self.anbima_debentures_service.get_anbima_debentures(db, reference_date)
        #     return jsonify(anbima_debentures)

        # except Exception as e:
        #     db.rollback()
        #     return jsonify({"error": str(e)}), 500

        # finally:
        #     # Garante que a sessão será encerrada
        #     db.close()



    def anbima_debentures(self, date: str):
        """Get anbima debentures endpoint"""
        return self.controllers["debentures"].get_anbima_debentures(date)