from flask import jsonify, request
from core.services.management_reports.monthly_tir_service import MonthlyTIRReportService
from core.services.token_service import TokenService
from utils.logging_requests import Logger
import traceback


class MonthlyTIRController:
    def __init__(self, app):
        self.monthly_tir_service = MonthlyTIRReportService()
        self.token_service = TokenService()
        self.app = app
        self.register_routes()
        self.logger = Logger(app)

    def register_routes(self):
        @self.app.route(
            "/api/v1/rg-monthly-tir", methods=["POST"], endpoint="rg_tir_handler"
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
                    "Iniciando requisição de relatório gerencial de TIR mensal."
                )
                response = self.monthly_tir_service.get_monthly_tir_report()

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
                            "error": "Falha ao iniciar a requisição de relatório gerencial de TIR mensal."
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

            csv_data = self.monthly_tir_service.process_csv_from_url(csv_url)
            if not csv_data:
                self.logger.logger.info(
                    "Não foram encontrados dados para o relatório de TIR mensal."
                )
                return (
                    jsonify(
                        {
                            "message": "Não foram encontrados dados para o relatório de TIR mensal."
                        }
                    ),
                    204,
                )

            self.logger.logger.info(f"Relatório de TIR mensal gerado com sucesso.")

            return jsonify(csv_data), 200
        except Exception as e:
            self.logger.logger.error(
                f"Erro ao processar o payload do webhook: {str(e)}"
            )
            self.logger.logger.error(traceback.format_exc())
            return jsonify({"error": "Internal server error"}), 500
