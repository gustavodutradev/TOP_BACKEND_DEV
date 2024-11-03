from dataclasses import dataclass
from typing import Optional, Dict, Any
from core.services.config_service import ConfigService
import json
import requests
import logging

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class APIResponse:
    """Classe para padronizar respostas da API."""

    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class RegistrationDataService:
    """Serviço para acessar dados cadastrais de contas."""

    def __init__(self) -> None:
        self.config_service = ConfigService()
        self._base_endpoint = (
            "/iaas-account-management/api/v1/account-management/account"
        )

    def _build_url(self, account_number: str) -> str:
        """Constrói a URL para a requisição."""
        return f"{self.config_service.base_url}{self._base_endpoint}/{account_number}/information"

    def _make_request(self, url: str) -> APIResponse:
        """Realiza a requisição HTTP e trata os erros."""
        try:
            headers = self.config_service.get_headers()
            response = requests.get(url, headers=headers, timeout=30)

            logger.info(f"Request to {url} - Status Code: {response.status_code}")

            if response.status_code != 200:
                error_msg = f"API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return APIResponse(success=False, error=error_msg)

            data = response.json()
            if not isinstance(data, dict):
                error_msg = "Invalid JSON response format"
                logger.error(error_msg)
                return APIResponse(success=False, error=error_msg)

            return APIResponse(success=True, data=data)

        except requests.exceptions.Timeout:
            error_msg = "Request timeout"
            logger.error(error_msg)
            return APIResponse(success=False, error=error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"Request error: {str(e)}"
            logger.error(error_msg)
            return APIResponse(success=False, error=error_msg)
        except json.JSONDecodeError as e:
            error_msg = f"JSON decode error: {str(e)}"
            logger.error(error_msg)
            return APIResponse(success=False, error=error_msg)

    def get_registration_data(self, account_number: str) -> Dict[str, Any]:
        """Busca todos os dados cadastrais de uma conta."""
        url = self._build_url(account_number)
        response = self._make_request(url)

        if not response.success:
            return {"error": response.error}

        return response.data

    def get_holder_name(self, account_number: str) -> str:
        """Busca apenas o nome do titular de uma conta."""
        response = self.get_registration_data(account_number)

        if "error" in response:
            logger.error(f"Error fetching holder name: {response['error']}")
            return "Nome não encontrado"

        try:
            return response["holder"]["name"]
        except KeyError as e:
            error_msg = f"Missing required field in response: {str(e)}"
            logger.error(error_msg)
            return "Nome não encontrado"
