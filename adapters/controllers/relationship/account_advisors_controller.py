from flask import jsonify, request
from core.services.relationship.account_advisors_service import RelationshipService
from core.services.token_service import TokenService
from utils.logging_requests import Logger
import traceback


class RelationshipController:
    def __init__(self, app):
        self.relationship_service = RelationshipService()
        self.token_service = TokenService()
        self.app = app
        self.register_routes()
        self.logger = Logger(app)

    def register_routes(self):
        @self.app.route(
            "/api/v1/relationship-accounts",
            methods=["POST"],
            endpoint="relationship_accounts_handler",
        )
        def handler():
            """Lida com a solicitação inicial e também processa webhooks."""
            try:
                if request.is_json:
                    data = request.get_json(silent=True)

                    if "response" in data:
                        self.logger.log_and_respond("Webhook recebido.")
                        return self._process_webhook(data)

                self.logger.log_and_respond(
                    "Iniciando requisição de contas vinculadas."
                )
                response = self.relationship_service.get_account_advisors_relationship()

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
                            "error": "Falha ao iniciar a requisição de contas vinculadas."
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

            linked_accounts = self.relationship_service.process_csv_from_url(csv_url)
            if not linked_accounts:
                self.logger.logger.info("Nenhuma conta vinculada encontrada.")
                return jsonify({"message": "Nenhuma conta vinculada encontrada."}), 204

            self.logger.logger.info(f"Contas vinculadas encontradas")

            return jsonify(linked_accounts), 200
        except Exception as e:
            self.logger.logger.error(
                f"Erro ao processar o payload do webhook: {str(e)}"
            )
            self.logger.logger.error(traceback.format_exc())
            return jsonify({"error": "Internal server error"}), 500