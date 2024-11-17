from flask import request
from core.services.fixed_income_reports.cra_cri_service import CraCriService
from core.services.token_service import TokenService
from utils.logging_requests import Logger
from typing import Dict, Tuple, Any
import traceback
from http import HTTPStatus


class CraCriController:
    def __init__(self, app):
        self.cra_cri_service = CraCriService()
        self.token_service = TokenService()
        self.app = app
        self.logger = Logger(app)
        self.register_routes()

    def register_routes(self) -> None:
        self.app.add_url_rule(
            "/api/v1/rf-cra-cri", "cra_cri_handler", self.handler, methods=["POST"]
        )

    def handler(self) -> Tuple[Dict[str, Any], int]:
        try:
            if not request.is_json:
                return self._handle_initial_request()

            data = request.get_json(silent=True)
            if not data:
                return {"error": "Invalid JSON payload"}, HTTPStatus.BAD_REQUEST

            return self._process_webhook(data)

        except Exception as e:
            return self._handle_error(e)

    def _handle_initial_request(self) -> Tuple[Dict[str, Any], int]:
        self.logger.log_and_respond("Iniciando requisição de relatório RF de CRA-CRI.")

        if not self.cra_cri_service.get_cra_cri_report():
            return {
                "error": "Falha ao iniciar a requisição de relatório RF de CRA-CRI."
            }, HTTPStatus.INTERNAL_SERVER_ERROR

        return {
            "message": "Requisição aceita. Aguardando processamento via webhook."
        }, HTTPStatus.ACCEPTED

    def _process_webhook(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        self.logger.log_and_respond("Webhook recebido.")

        # Verificar se há erros no webhook
        if "errors" in data:
            error_message = self._extract_error_message(data)
            self.logger.logger.error(f"Erro no webhook: {error_message}")
            return {"error": error_message}, HTTPStatus.INTERNAL_SERVER_ERROR

        csv_url = self._extract_csv_url(data)
        if not csv_url:
            self.logger.logger.error("URL do CSV não encontrada no payload.")
            self.logger.logger.error(f"Payload recebido: {data}")
            return {"error": "CSV URL not found in payload"}, HTTPStatus.BAD_REQUEST

        csv_data = self.cra_cri_service.process_csv_from_url(csv_url)
        if not csv_data:
            self.logger.logger.info(
                "Não foram encontrados dados para o relatório RF de CRA-CRI."
            )
            return {
                "message": "Não foram encontrados dados para o relatório RF de CRA-CRI."
            }, HTTPStatus.NO_CONTENT

        self.logger.logger.info("Relatório de CRA-CRI gerado com sucesso.")
        return csv_data, HTTPStatus.OK

    def _extract_csv_url(self, data: Dict[str, Any]) -> str:
        """
        Extract CSV URL from webhook payload with enhanced logging.
        """
        # Tentar extrair URL do formato padrão
        url = data.get("url")
        if url:
            self.logger.logger.info("URL encontrada no formato padrão")
            return url

        # Tentar extrair URL do objeto response
        response_data = data.get("response", {})
        url = response_data.get("url")
        if url:
            self.logger.logger.info("URL encontrada no objeto response")
            return url

        # Log detalhado quando URL não é encontrada
        self.logger.logger.error(f"Estrutura do payload recebido: {data}")
        return ""

    def _extract_error_message(self, data: Dict[str, Any]) -> str:
        """
        Extract error message from webhook payload.
        """
        if "errors" in data and data["errors"]:
            error = data["errors"][0]
            return f"Error {error.get('code')}: {error.get('message')}"
        return "Unknown error in webhook response"

    def _handle_error(self, error: Exception) -> Tuple[Dict[str, Any], int]:
        self.logger.logger.error(f"Erro na requisição: {str(error)}")
        self.logger.logger.error(traceback.format_exc())
        return {"error": "Internal server error"}, HTTPStatus.INTERNAL_SERVER_ERROR
