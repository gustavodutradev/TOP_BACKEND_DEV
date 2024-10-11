from flask import jsonify
from core.services.stock_orders_service import StockOrdersService
from utils.logging import Logger


class StockOrdersController:

    def __init__(self, app) -> None:
        self.orders_service = StockOrdersService()
        self.app = app
        self.register_routes()
        self.Logger = Logger()

    def register_routes(self):
        @self.app.route("/api/v1/orders", methods=["POST"])
        def orders():
            try:
                # Loga o recebimento da requisição
                Logger.log_and_respond("Pending Stock Orders")

                # Obtém as ordens pendentes de aprovação
                pending_orders = self.orders_service.get_stock_orders()

                # Caso não tenha ordens pendentes, retorna 204 (No Content)
                if not pending_orders:
                    return (
                        jsonify({"message": "Nenhuma ordem pendente encontrada."}),
                        204,
                    )

                # Caso tenha ordens, retorna as ordens em formato JSON
                return jsonify(pending_orders), 200

            except Exception as e:
                # Retorna um erro genérico caso algo dê errado
                return jsonify({"error": str(e)}), 500
