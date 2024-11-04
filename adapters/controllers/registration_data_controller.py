from typing import Tuple
from flask import jsonify, Response
from http import HTTPStatus
import logging
from functools import wraps
from core.services.registration_data_service import RegistrationDataService


def handle_exceptions(func):
    """
    Decorator para tratamento padronizado de exceções nas rotas.
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Tuple[Response, int]:
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            logging.error(f"Validation error: {str(e)}")
            return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
        except Exception as e:
            logging.error(f"Error processing request: {str(e)}", exc_info=True)
            return (
                jsonify({"error": "An unexpected error occurred"}),
                HTTPStatus.INTERNAL_SERVER_ERROR
            )
    return wrapper


class RegistrationDataController:
    """
    Controlador para gerenciar endpoints relacionados a dados cadastrais.
    
    Attributes:
        app: Instância da aplicação Flask
        registration_data_service: Serviço para operações com dados cadastrais
    """

    def __init__(self, app) -> None:
        self.app = app
        self.registration_data_service = RegistrationDataService()
        self._setup_routes()

    def _setup_routes(self) -> None:
        """Configura as rotas do controlador."""
        routes = [
            {
                "rule": "/api/v1/get-registration-data/<account_number>",
                "endpoint": "get_registration_data_handler",
                "view_func": self.get_registration_data,
                "methods": ["GET"]
            },
            {
                "rule": "/api/v1/get-holder-name/<account_number>",
                "endpoint": "get_holder_name_handler",
                "view_func": self.get_holder_name,
                "methods": ["GET"]
            }
        ]

        for route in routes:
            self.app.add_url_rule(**route)

    @handle_exceptions
    def get_registration_data(self, account_number: str) -> Tuple[Response, int]:
        """
        Retorna todos os dados cadastrais da conta.

        Args:
            account_number: Número da conta do cliente

        Returns:
            Response: JSON com os dados cadastrais
            int: Código HTTP de status

        Raises:
            ValueError: Se o número da conta for inválido
            Exception: Para outros erros não esperados
        """
        self._validate_account_number(account_number)
        registration_data = self.registration_data_service.get_registration_data(
            account_number
        )
        return jsonify(registration_data), HTTPStatus.OK

    @handle_exceptions
    def get_holder_name(self, account_number: str) -> Tuple[Response, int]:
        """
        Retorna o nome do titular da conta.

        Args:
            account_number: Número da conta do cliente

        Returns:
            Response: JSON com o nome do titular
            int: Código HTTP de status

        Raises:
            ValueError: Se o número da conta for inválido
            Exception: Para outros erros não esperados
        """
        self._validate_account_number(account_number)
        holder_name = self.registration_data_service.get_holder_name(account_number)
        return jsonify({"holder_name": holder_name}), HTTPStatus.OK

    @staticmethod
    def _validate_account_number(account_number: str) -> None:
        """
        Valida o formato do número da conta.

        Args:
            account_number: Número da conta a ser validado

        Raises:
            ValueError: Se o número da conta estiver em formato inválido
        """
        if not account_number or not account_number.strip():
            raise ValueError("Account number cannot be empty")
        if not account_number.isdigit():
            raise ValueError("Account number must contain only digits")