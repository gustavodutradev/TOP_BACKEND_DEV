from flask import jsonify
from core.services.stock_orders_service import StockOrdersService
from core.services.token_service import TokenService
from utils.logging import Logger
import traceback
import time

class StockOrdersController:

    def __init__(self, app) -> None:
        self.orders_service = StockOrdersService()
        self.token_service = TokenService()
        self.app = app
        self.register_routes()
        self.logger = Logger(app)

    def register_routes(self):
        @self.app.route("/api/v1/orders", methods=["POST"])
        def orders():
            try:
                # Loga o início do processamento da requisição
                self.logger.log_and_respond("Pending Stock Orders - Request Received")

                # Obtém as ordens pendentes de aprovação
                pending_orders = self.orders_service.get_stock_orders()

                time.sleep(10)

                # Caso não tenha ordens pendentes, retorna 204 (No Content)
                if not pending_orders:
                    self.logger.logger.info("Nenhuma ordem pendente encontrada.")
                    return jsonify({"message": "Nenhuma ordem pendente encontrada."}), 204

                # Caso tenha ordens, retorna as ordens em formato JSON
                self.logger.logger.info(f"Ordens pendentes encontradas: {pending_orders}")
                return jsonify(pending_orders), 200

            except Exception as e:
                # Loga a exceção com detalhes
                self.logger.logger.error(f"Erro ao processar ordens pendentes: {str(e)}")
                self.logger.logger.error(traceback.format_exc())

                # Retorna um erro genérico com status 500
                return jsonify({"error": "Internal server error"}), 500
