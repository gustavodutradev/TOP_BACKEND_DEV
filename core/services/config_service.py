import uuid
from dataclasses import dataclass
from typing import Optional
from core.services.token_service import TokenService

@dataclass
class ApiConfig:
    """Classe para armazenar configurações da API."""
    base_url: str = "https://api.btgpactual.com"
    content_type: str = "application/json"
    accept: str = "*/*"

class ConfigService:
    """
    Serviço de configuração que gerencia headers e tokens para requisições à API.
    Implementa o padrão Singleton para garantir uma única instância.
    """
    _instance: Optional['ConfigService'] = None
    
    def __new__(cls) -> 'ConfigService':
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if not self._initialized:
            self._initialize()
            self._initialized = True

    def _initialize(self) -> None:
        """Inicializa os atributos necessários do serviço."""
        self._token_service = TokenService()
        self._config = ApiConfig()
        self._request_id = uuid.uuid4()
        self._token: Optional[str] = None
        self._update_token()

    def _update_token(self) -> None:
        """
        Atualiza o token de acesso.
        Raises:
            ValueError: Se não for possível obter um token válido.
        """
        token = self._token_service.get_token()
        
        if not token:
            raise ValueError("Não foi possível obter um token de acesso válido.")
            
        self._token = token

    def get_headers(self) -> dict:
        """
        Retorna os headers necessários para as requisições à API.
        Returns:
            dict: Headers da requisição com token atualizado.
        """
        self._update_token()
        
        return {
            "Content-Type": self._config.content_type,
            "Accept": self._config.accept,
            "x-id-partner-request": str(self._request_id),
            "access_token": self._token
        }

    @property
    def base_url(self) -> str:
        """Retorna a URL base da API."""
        return self._config.base_url