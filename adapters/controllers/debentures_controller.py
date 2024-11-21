from flask import jsonify, request
from core.services.debentures_service import AnbimaDebenturesService
from database.connection import get_db  # Assumindo que você tenha um método para obter a sessão do DB

class AnbimaDebenturesController:
    def __init__(self):
        self.anbima_debentures_service = AnbimaDebenturesService()

    def get_anbima_debentures(self):
        # Obtém os dados da requisição JSON
        data = request.get_json()
        reference_date = data.get("reference_date")

        if not reference_date:
            return jsonify({"error": "Data de referência não fornecida."}), 400

        # Obtém a sessão do banco de dados
        db = next(get_db())

        try:
            # Chama o serviço que retorna e persiste os dados
            anbima_debentures = self.anbima_debentures_service.get_anbima_debentures(db, reference_date)
            return jsonify(anbima_debentures)

        except Exception as e:
            db.rollback()
            return jsonify({"error": str(e)}), 500

        finally:
            # Garante que a sessão será encerrada
            db.close()
