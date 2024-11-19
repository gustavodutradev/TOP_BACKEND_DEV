from flask import request
from core.services.fixed_income_reports.fixed_income_service import FixedIncomeService
from core.services.token_service import TokenService
from utils.logging_requests import Logger
from typing import Dict, Tuple, Any
import traceback
from http import HTTPStatus


class FixedIncomeController:
    def __init__(self, app):
        self.fixed_income_service = FixedIncomeService()
        self.token_service = TokenService()
        self.app = app
        self.logger = Logger(app)
        self.register_routes()

    def register_routes(self) -> None:
        """Register the API routes for the controller."""
        self.app.add_url_rule(
            "/api/v1/rf-fixed-income",
            "fixed_income_handler",
            self.handler,
            methods=["POST"],
        )

    def handler(self) -> Tuple[Dict[str, Any], int]:
        """
        Handle the initial request and process webhooks.
        Returns:
            Tuple containing response data and HTTP status code
        """
        try:
            if not request.is_json:
                return self._handle_initial_request()

            data = request.get_json(silent=True)
            if data and "response" in data:
                return self._process_webhook(data)

            return self._handle_initial_request()

        except Exception as e:
            return self._handle_error(e)

    def _handle_initial_request(self) -> Tuple[Dict[str, Any], int]:
        """
        Handle the initial report request.
        Returns:
            Tuple containing response data and HTTP status code
        """
        self.logger.log_and_respond(
            "Iniciando requisição de relatório RF por parceiro."
        )

        if not self.fixed_income_service.get_fixed_income_report():
            return {
                "error": "Falha ao iniciar a requisição de relatório RF por parceiro."
            }, HTTPStatus.INTERNAL_SERVER_ERROR

        return {
            "message": "Requisição aceita. Aguardando processamento via webhook."
        }, HTTPStatus.ACCEPTED

    def _process_webhook(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Process the webhook payload from the API.
        Args:
            data: The webhook payload data
        Returns:
            Tuple containing response data and HTTP status code
        """
        self.logger.log_and_respond("Webhook recebido.")

        csv_url = self._extract_csv_url(data)
        if not csv_url:
            self.logger.logger.error("URL do CSV não encontrada no payload.")
            return {"error": "CSV URL not found."}, HTTPStatus.BAD_REQUEST

        try:
            csv_data = self.fixed_income_service.process_csv_from_url(csv_url)
        except Exception as e:
            self.logger.logger.error(f"Erro ao processar CSV: {str(e)}")
            return {"error": "Erro ao processar CSV"}, HTTPStatus.INTERNAL_SERVER_ERROR

        if not csv_data:
            self.logger.logger.info(
                "Não foram encontrados dados para o relatório RF por parceiro."
            )
            return {
                "message": "Não foram encontrados dados para o relatório RF por parceiro."
            }, HTTPStatus.NO_CONTENT

        self.logger.logger.info("Relatório de Renda Fixa gerado com sucesso.")
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

    def _handle_error(self, error: Exception) -> Tuple[Dict[str, Any], int]:
        """
        Handle and log any exceptions that occur during processing.
        Args:
            error: The exception that occurred
        Returns:
            Tuple containing error response and HTTP status code
        """
        self.logger.logger.error(f"Erro na requisição: {str(error)}")
        self.logger.logger.error(traceback.format_exc())
        return {"error": "Internal server error"}, HTTPStatus.INTERNAL_SERVER_ERROR
