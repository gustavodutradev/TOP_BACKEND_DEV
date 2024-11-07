from flask import request
from core.services.custody.custody_service import CustodyService
from core.services.token_service import TokenService
from utils.logging_requests import Logger
from typing import Dict, Tuple, Any
import traceback
from http import HTTPStatus


class CustodyController:
    def __init__(self, app):
        self.custody_service = CustodyService()
        self.token_service = TokenService()
        self.app = app
        self.logger = Logger(app)
        self.register_routes()

    def register_routes(self) -> None:
        """Register the API routes for the controller."""
        self.app.add_url_rule(
            "/api/v1/custody", "rg_custody_handler", self.handler, methods=["POST"]
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
        Handle the initial Custody report request.
        Returns:
            Tuple containing response data and HTTP status code
        """
        self.logger.log_and_respond("Iniciando requisição de relatório de Custódia.")

        if not self.custody_service.get_custody():
            return {
                "error": "Falha ao iniciar a requisição de relatório de Custódia."
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

        # Processamento do CSV e envio de e-mails de produtos estruturados com vencimento
        self.logger.log_and_respond("Processando relatório de Custódia e verificando vencimento de produtos estruturados.")
        try:
            # Executa a verificação e envio de notificações sobre vencimentos
            self.custody_service.execute_daily_expiration_check(csv_url)
            self.logger.logger.info("Relatório de Custódia processado e e-mails de notificação enviados com sucesso.")
            return {"message": "Relatório processado e e-mails enviados."}, HTTPStatus.OK
        except Exception as e:
            self.logger.logger.error(f"Erro ao processar o CSV ou enviar e-mails: {str(e)}")
            self.logger.logger.error(traceback.format_exc())
            return {"error": "Erro ao processar o relatório de Custódia ou enviar e-mails."}, HTTPStatus.INTERNAL_SERVER_ERROR

    def _extract_csv_url(self, data: Dict[str, Any]) -> str:
        """
        Extract CSV URL from webhook payload, supporting multiple payload formats.
        Args:
            data: The webhook payload data
        Returns:
            The CSV URL if found, empty string otherwise
        """
        # Tenta obter URL da chave 'response' ou 'result'
        return data.get("response", {}).get("url", "") or data.get("result", {}).get("url", "")

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
