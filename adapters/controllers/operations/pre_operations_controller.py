from flask import request
from core.services.operations.pre_operations_service import PreOperationsService
from core.services.token_service import TokenService
from utils.logging_requests import Logger
from typing import Dict, Tuple, Any
import traceback
from http import HTTPStatus


class PreOperationsController:
    def __init__(self, app):
        self.pre_operations_service = PreOperationsService()
        self.token_service = TokenService()
        self.app = app
        self.logger = Logger(app)
        self.register_routes()

    def register_routes(self) -> None:
        """Register the API routes for the controller."""
        self.app.add_url_rule(
            "/api/v1/pre-operations",
            "pre_operations_handler",
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
        Handle the initial Pre-Operations report request.
        Returns:
            Tuple containing response data and HTTP status code
        """
        self.logger.log_and_respond(
            "Iniciando requisição do relatório de todas Pré-Operações do parceiro"
        )

        if not self.pre_operations_service.get_pre_operations_report():
            return {
                "error": "Falha ao iniciar a requisição do relatório de todas Pré-Operações do parceiro"
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

        csv_data = self.pre_operations_service.process_csv_from_url(csv_url)
        if not csv_data:
            self.logger.logger.info(
                "Não foram encontrados dados para o relatório de todas Pré-Operações do parceiro."
            )
            return {
                "message": "Não foram encontrados dados para o relatório de todas Pré-Operações do parceiro."
            }, HTTPStatus.NO_CONTENT

        self.logger.logger.info(
            "relatório de todas Pré-Operações do parceiro gerado com sucesso."
        )
        return csv_data, HTTPStatus.OK

    def _extract_csv_url(self, data: Dict[str, Any]) -> str:
        """
        Extract CSV URL from webhook payload.
        Args:
            data: The webhook payload data
        Returns:
            The CSV URL if found, empty string otherwise
        """
        return data.get("response", {}).get("url", "")

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