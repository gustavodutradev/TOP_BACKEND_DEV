from flask import jsonify, request
from core.services.stock_orders_service import StockOrdersService
from core.services.token_service import TokenService
from utils.logging_requests import Logger
import traceback


class StockOrdersController:
    def __init__(self, app) -> None:
        self.orders_service = StockOrdersService()
        self.token_service = TokenService()
        self.app = app
        self.register_routes()
        self.logger = Logger(app)

    def register_routes(self):
        @self.app.route("/api/v1/orders", methods=["POST"])
        def orders_handler():
            """Lida com a solicitação inicial e também processa webhooks."""
            try:
                # Detecta se é uma chamada inicial ou um webhook com base no payload recebido.
                if request.is_json:
                    data = request.get_json(force=True)

                    # Se 'result' estiver presente, trata como um webhook.
                    if "result" in data:
                        self.logger.log_and_respond("Webhook recebido.")
                        return self._process_webhook(data)

                # Se não for webhook, é a requisição inicial para buscar ordens.
                self.logger.log_and_respond("Iniciando requisição de ordens pendentes.")
                response = self.orders_service.get_stock_orders()

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
                    jsonify({"error": "Falha ao iniciar a requisição de ordens."}),
                    500,
                )

            except Exception as e:
                self.logger.logger.error(f"Erro na requisição: {str(e)}")
                self.logger.logger.error(traceback.format_exc())
                return jsonify({"error": "Internal server error"}), 500

    def _process_webhook(self, data):
        """Processa o payload enviado pela API via webhook."""
        try:
            # Tenta capturar a URL do CSV dentro do payload do webhook.
            csv_url = data.get("result", {}).get("url")
            if not csv_url:
                self.logger.logger.error("URL do CSV não encontrada no payload.")
                return jsonify({"error": "CSV URL not found."}), 400
            # Processa as ordens a partir do CSV obtido.
            pending_orders = self.orders_service.process_csv_from_url(csv_url)
            if not pending_orders:
                self.logger.logger.info("Nenhuma ordem pendente encontrada.")
                return jsonify({"message": "Nenhuma ordem pendente encontrada."}), 204
            # Loga e retorna as ordens encontradas.
            self.logger.logger.info(f"Ordens pendentes encontradas: {pending_orders}")
            # Envia um email com as ordens pendentes.
            self.orders_service.send_pending_orders_email(pending_orders)
            # Retorna as ordens em formato JSON.
            return jsonify(pending_orders), 200
        except Exception as e:
            self.logger.logger.error(
                f"Erro ao processar o payload do webhook: {str(e)}"
            )
            self.logger.logger.error(traceback.format_exc())
            return jsonify({"error": "Internal server error"}), 500
