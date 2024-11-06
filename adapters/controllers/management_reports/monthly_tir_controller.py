from flask import request
from core.services.management_reports.monthly_tir_service import MonthlyTIRReportService
from core.services.token_service import TokenService
from utils.logging_requests import Logger
from typing import Dict, Tuple, Any
import traceback
from http import HTTPStatus


class MonthlyTIRController:
    def __init__(self, app):
        self.monthly_tir_service = MonthlyTIRReportService()
        self.token_service = TokenService()
        self.app = app
        self.logger = Logger(app)
        self.register_routes()

    def register_routes(self) -> None:
        """Register the API routes for the controller."""
        self.app.add_url_rule(
            "/api/v1/rg-monthly-tir", "rg_tir_handler", self.handler, methods=["POST"]
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
        Handle the initial TIR report request.
        Returns:
            Tuple containing response data and HTTP status code
        """
        self.logger.log_and_respond(
            "Iniciando requisição de relatório gerencial de TIR mensal."
        )

        if not self.monthly_tir_service.get_monthly_tir_report():
            return {
                "error": "Falha ao iniciar a requisição de relatório gerencial de TIR mensal."
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
        # Log do payload completo para debug
        self.logger.logger.info("Webhook recebido com payload completo: %s", data)

        try:
            # Primeiro, vamos verificar se é um webhook de erro
            if "error" in str(data).lower():
                self.logger.logger.error("Webhook de erro recebido: %s", data)
                return {"error": "Webhook error received"}, HTTPStatus.BAD_REQUEST

            # Extrai a URL do CSV com logging detalhado
            csv_url = self._extract_csv_url(data)
            self.logger.logger.info("URL extraída do webhook: %s", csv_url)

            if not csv_url:
                self.logger.logger.error(
                    "URL do CSV não encontrada no payload. Payload completo: %s", data
                )
                return {"error": "CSV URL not found."}, HTTPStatus.BAD_REQUEST

            # Valida a URL antes de processá-la
            if not self._validate_url(csv_url):
                self.logger.logger.error(
                    "URL inválida recebida: %s. Payload completo: %s", csv_url, data
                )
                return {"error": "Invalid CSV URL format."}, HTTPStatus.BAD_REQUEST

            csv_data = self.monthly_tir_service.process_csv_from_url(csv_url)
            if not csv_data:
                self.logger.logger.info(
                    "Não foram encontrados dados para o relatório de TIR mensal. URL: %s",
                    csv_url,
                )
                return {
                    "message": "Não foram encontrados dados para o relatório de TIR mensal."
                }, HTTPStatus.NO_CONTENT

            self.logger.logger.info(
                "Relatório de TIR mensal gerado com sucesso para URL: %s", csv_url
            )
            return csv_data, HTTPStatus.OK

        except Exception as e:
            self.logger.logger.error(
                "Erro ao processar webhook: %s. Payload: %s", str(e), data
            )
            self.logger.logger.error(traceback.format_exc())
            return {"error": str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

    def _extract_csv_url(self, data: Dict[str, Any]) -> str:
        """
        Extract CSV URL from webhook payload with detailed logging.
        Args:
            data: The webhook payload data
        Returns:
            The CSV URL if found, empty string otherwise
        """
        self.logger.logger.debug("Iniciando extração de URL do payload: %s", data)

        try:
            # Se o payload contiver um objeto response
            if isinstance(data.get("response"), dict):
                url = data["response"].get("url")
                self.logger.logger.debug(
                    "URL encontrada em ['response']['url']: %s", url
                )
                if url:
                    return url

            # Se o payload contiver um objeto result
            if isinstance(data.get("result"), dict):
                url = data["result"].get("url")
                self.logger.logger.debug("URL encontrada em ['result']['url']: %s", url)
                if url:
                    return url

            # Busca direta por url no payload
            url = data.get("url")
            self.logger.logger.debug("URL encontrada diretamente no payload: %s", url)
            if url:
                return url

            # Busca em outros possíveis caminhos do payload
            if isinstance(data.get("data"), dict):
                url = data["data"].get("url")
                self.logger.logger.debug("URL encontrada em ['data']['url']: %s", url)
                if url:
                    return url

            # Se chegou aqui, não encontrou URL
            self.logger.logger.warning("Nenhuma URL encontrada no payload: %s", data)
            return ""

        except Exception as e:
            self.logger.logger.error(
                "Erro ao extrair URL do payload: %s. Payload: %s", str(e), data
            )
            return ""

    def _validate_url(self, url: str) -> bool:
        """
        Validate if URL is well-formed and has a proper scheme.
        Args:
            url: URL to validate
        Returns:
            bool indicating if URL is valid
        """
        from urllib.parse import urlparse

        try:
            self.logger.logger.debug("Validando URL: %s", url)

            if not url:
                self.logger.logger.error("URL vazia")
                return False

            parsed = urlparse(url)
            is_valid = all([parsed.scheme in ["http", "https"], parsed.netloc])

            if not is_valid:
                self.logger.logger.error(
                    "URL inválida. Scheme: %s, NetLoc: %s", parsed.scheme, parsed.netloc
                )

            return is_valid

        except Exception as e:
            self.logger.logger.error("Erro ao validar URL %s: %s", url, str(e))
            return False

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
