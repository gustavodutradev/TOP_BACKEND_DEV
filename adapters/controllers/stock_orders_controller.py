from flask import jsonify, request
from core.services.stock_orders_service import StockOrdersService
from core.services.token_service import TokenService
from utils.logging_requests import Logger
from typing import Dict, Tuple, Any
from http import HTTPStatus
import traceback


class StockOrdersController:
    def __init__(self, app) -> None:
        self.orders_service = StockOrdersService()
        self.token_service = TokenService()
        self.app = app
        self.register_routes()
        self.logger = Logger(app)

    def register_routes(self) -> None:
        """Registra a rota da API para o controller."""
        self.app.add_url_rule(
            "/api/v1/orders", "stock_orders_handler", self.handler, methods=["POST"]
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
            if data and "result" in data:
                return self._process_webhook(data)

            return self._handle_initial_request()

        except Exception as e:
            return self._handle_error(e)

    def _handle_initial_request(self) -> Tuple[Dict[str, Any], int]:
        """
        Lida com a requisição inicial de Ordens da Bolsa.
        Returns:
            Tupla contendo dados de resposta e status HTTP
        """
        self.logger.log_and_respond("Iniciando requisição de ordens.")

        if not self.orders_service.get_stock_orders():
            return {
                "error": "Falha ao iniciar a requisição de ordens."
            }, HTTPStatus.INTERNAL_SERVER_ERROR

        return {
            "message": "Requisição aceita. Aguardando processamento via webhook."
        }, HTTPStatus.ACCEPTED

    def _process_webhook(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Processa o payload do webhook que vem da API.
        Args:
            data: Webhook payload
        Returns:
            Tupla contento dados de resposta e status HTTP
        """
        self.logger.log_and_respond("Webhook recebido.")

        csv_url = self._extract_csv_url(data)
        if not csv_url:
            self.logger.logger.error("URL do CSV não encontrada no payload.")
            return {"error": "CSV URL not found."}, HTTPStatus.BAD_REQUEST

        pending_orders = self.orders_service.process_csv_from_url(csv_url)
        if not pending_orders:
            self.logger.logger.info(
                "Nenhuma ordem pendente encontrada."
            )
            self.orders_service.send_empty_pending_orders_email()
            return {
                "message": "Nenhuma ordem pendente encontrada."
            }, HTTPStatus.NO_CONTENT

        self.logger.logger.info(f"Ordens pendentes encontradas")

        self.orders_service.send_pending_orders_email(pending_orders)
        return pending_orders, HTTPStatus.OK

    def _extract_csv_url(self, data: Dict[str, Any]) -> str:
        """
        Extrai a URL do CSV do payload do webhook.
        Args:
            data: webhook payload
        Returns:
           A URL do CSV caso encontrada, se não, uma string vazia
        """
        return data.get("response", {}).get("url", "")

    def _handle_error(self, error: Exception) -> Tuple[Dict[str, Any], int]:
        """
        Lida e loga qualquer exceção que ocorrer durante o processo.
        Args:
            error: A exceção que ocorreu
        Returns:
            Tupla contendo resposta e status do erro
        """
        self.logger.logger.error(f"Erro na requisição: {str(error)}")
        self.logger.logger.error(traceback.format_exc())
        return {"error": "Internal server error"}, HTTPStatus.INTERNAL_SERVER_ERROR
