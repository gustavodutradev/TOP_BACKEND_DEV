from flask import jsonify, request
from core.services.stock_orders_service import StockOrdersService
from core.services.token_service import TokenService
from utils.logging_requests import Logger
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
                pending_orders = self.orders_service.get_stock_orders()
                
                
                self.logger.log_and_respond("Pending Stock Orders - Request Received")


                if not pending_orders:
                    self.logger.logger.info("Nenhuma ordem pendente encontrada.")
                    return (
                        jsonify({"message": "Nenhuma ordem pendente encontrada."}),
                        204,
                    )

                # Caso tenha ordens, retorna as ordens em formato JSON
                self.logger.logger.info(
                    f"Ordens pendentes encontradas: {pending_orders}"
                )
                return jsonify(pending_orders), 200

            except Exception as e:
                self.logger.logger.error(
                    f"Erro ao processar ordens pendentes: {str(e)}"
                )
                self.logger.logger.error(traceback.format_exc())

                # Retorna um erro genérico com status 500
                return jsonify({"error": "Internal server error"}), 500
