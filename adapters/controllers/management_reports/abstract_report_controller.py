from abc import ABC, abstractmethod
from flask import request
from typing import Dict, Tuple, Any
from http import HTTPStatus
import traceback
from utils.logging_requests import Logger
from core.services.token_service import TokenService


class AbstractReportController(ABC):
    """
    Classe base abstrata para controladores de relatórios.
    Fornece a estrutura comum e implementação base para processamento de relatórios.
    """

    def __init__(self, app, endpoint: str, route: str):
        """
        Inicializa o controlador com configurações básicas.

        Args:
            app: A aplicação Flask
            endpoint: O endpoint para a rota
            route: A rota da API
        """
        self.app = app
        self.endpoint = endpoint
        self.route = route
        self.token_service = TokenService()
        self.logger = Logger(app)
        self.register_routes()

    @property
    @abstractmethod
    def report_name(self) -> str:
        """Nome do relatório para uso em mensagens de log e respostas."""
        pass

    @abstractmethod
    def get_report_service(self):
        """Retorna o serviço específico para processamento do relatório."""
        pass

    def register_routes(self) -> None:
        """Registra as rotas da API para o controlador."""
        self.app.add_url_rule(self.route, self.endpoint, self.handler, methods=["POST"])

    def handler(self) -> Tuple[Dict[str, Any], int]:
        """
        Manipula a requisição inicial e processa webhooks.
        Returns:
            Tuple contendo dados de resposta e código HTTP
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
        Manipula a requisição inicial do relatório.
        Returns:
            Tuple contendo dados de resposta e código HTTP
        """
        self.logger.log_and_respond(
            f"Iniciando requisição de relatório gerencial {self.report_name}."
        )

        service = self.get_report_service()
        if not service.generate_report():
            return {
                "error": f"Falha ao iniciar a requisição de relatório gerencial {self.report_name}."
            }, HTTPStatus.INTERNAL_SERVER_ERROR

        return {
            "message": "Requisição aceita. Aguardando processamento via webhook."
        }, HTTPStatus.ACCEPTED

    def _process_webhook(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Processa o payload do webhook da API.
        Args:
            data: Os dados do payload do webhook
        Returns:
            Tuple contendo dados de resposta e código HTTP
        """
        self.logger.log_and_respond("Webhook recebido.")

        csv_url = self._extract_csv_url(data)
        if not csv_url:
            self.logger.logger.error("URL do CSV não encontrada no payload.")
            return {"error": "CSV URL not found."}, HTTPStatus.BAD_REQUEST

        service = self.get_report_service()
        csv_data = service.process_csv_from_url(csv_url)
        if not csv_data:
            self.logger.logger.info(
                f"Não foram encontrados dados para o relatório {self.report_name}."
            )
            return {
                "message": f"Não foram encontrados dados para o relatório {self.report_name}."
            }, HTTPStatus.NO_CONTENT

        self.logger.logger.info(f"Relatório {self.report_name} gerado com sucesso.")
        return csv_data, HTTPStatus.OK

    def _extract_csv_url(self, data: Dict[str, Any]) -> str:
        """
        Extrai a URL do CSV do payload do webhook.
        Args:
            data: Os dados do payload do webhook
        Returns:
            A URL do CSV se encontrada, string vazia caso contrário
        """
        return data.get("response", {}).get("url", "")

    def _handle_error(self, error: Exception) -> Tuple[Dict[str, Any], int]:
        """
        Manipula e registra quaisquer exceções que ocorram durante o processamento.
        Args:
            error: A exceção que ocorreu
        Returns:
            Tuple contendo resposta de erro e código HTTP
        """
        self.logger.logger.error(f"Erro na requisição: {str(error)}")
        self.logger.logger.error(traceback.format_exc())
        return {"error": "Internal server error"}, HTTPStatus.INTERNAL_SERVER_ERROR
