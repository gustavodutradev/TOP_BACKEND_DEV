from flask import jsonify, request
from core.services.monthly_customer_profit_service import MonthlyCustomerProfitService
from core.services.token_service import TokenService
from utils.logging_requests import Logger
import traceback


class MonthlyCustomerProfitController:
    def __init__(self, app):
        self.monthly_customer_profit_service = MonthlyCustomerProfitService()
        self.token_service = TokenService()
        self.app = app
        self.register_routes()
        self.logger = Logger(app)

    def register_routes(self):
        @self.app.route("/api/v1/monthly-customer-profit", methods=["POST"])
        def handler():
            """Lida com a solicitação inicial e também processa webhooks."""
            try:
                if request.is_json:
                    data = request.get_json(silent=True)

                    if "response" in data:
                        self.logger.log_and_respond("Webhook recebido.")
                        return self._process_webhook(data)
                self.logger.log_and_respond(
                    "Iniciando requisição de rentabilidade mensal dos clientes."
                )
                response = self.monthly_customer_profit_service.getProfitByPeriod()

                if response:
                    return (
                        jsonify(
                            {
                                "message": "Requisição aceita. Aguardando processamento via webhook."
                            }
                        ),
                        202,
                    )

                return (
                    jsonify(
                        {
                            "error": "Falha ao iniciar a requisição de rentabilidade mensal dos clientes."
                        }
                    ),
                    500,
                )

            except Exception as e:
                self.logger.logger.error(f"Erro na requisição: {str(e)}")
                self.logger.logger.error(traceback.format_exc())
                return jsonify({"error": "Internal server error"}), 500

    def _process_webhook(self, data):
        """Processa o payload enviado pela API via webhook."""
        try:

            csv_url = data.get("response", {}).get("url")
            if not csv_url:
                self.logger.logger.error("URL do CSV não encontrada no payload.")
                return jsonify({"error": "CSV URL not found."}), 400

            pending_orders = self.orders_service.process_csv_from_url(csv_url)
            if not pending_orders:
                self.logger.logger.info("Nenhuma ordem pendente encontrada.")
                self.orders_service.send_empty_pending_orders_email()
                return jsonify({"message": "Nenhuma ordem pendente encontrada."}), 204

            self.logger.logger.info(f"Ordens pendentes encontradas: {pending_orders}")

            self.orders_service.send_pending_orders_email(pending_orders)

            return jsonify(pending_orders), 200
        except Exception as e:
            self.logger.logger.error(
                f"Erro ao processar o payload do webhook: {str(e)}"
            )
            self.logger.logger.error(traceback.format_exc())
            return jsonify({"error": "Internal server error"}), 500

