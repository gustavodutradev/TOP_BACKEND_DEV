from flask import request
from core.services.management_reports.positions_service import PositionReportService
from core.services.token_service import TokenService
from utils.logging_requests import Logger
from typing import Dict, Tuple, Any
import traceback
from http import HTTPStatus


class PositionReportController:
    def __init__(self, app):
        self.position_report_service = PositionReportService()
        self.token_service = TokenService()
        self.app = app
        self.logger = Logger(app)
        self.routes()

    def routes(self) -> None:
        """Register the API routes for the controller."""
        self.app.add_url_rule(
            "/api/v1/rg-posicoes", "rg_posicoes_handler", self.handler, methods=["POST"]
        )

    def handler(self) -> Tuple[Dict[str, Any], int]:
        """
        Lida com a requisição inicial e processa webhook.
        Returns:
            Tupla contendo dados de resposta e status HTTP
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
        Handle the initial Positions report request.
        Returns:
            Tuple containing response data and HTTP status code
        """
        self.logger.log_and_respond(
            "Iniciando requisição de relatório gerencial de Posições."
        )

        if not self.position_report_service.get_positions_report():
            return {
                "error": "Falha ao iniciar a requisição de relatório gerencial de Posições."
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

        csv_data = self.position_report_service.process_csv_from_url(csv_url)
        if not csv_data:
            self.logger.logger.info(
                "Não foram encontrados dados para o relatório de Posições."
            )
            return {
                "message": "Não foram encontrados dados para o relatório de Posições."
            }, HTTPStatus.NO_CONTENT

        self.logger.logger.info("Relatório de Posições gerado com sucesso.")
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
