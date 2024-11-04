from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import requests
import uuid
import time
import json
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TokenData:
    """Classe para armazenar dados do token."""

    access_token: str
    expires_at: float

    @property
    def is_expired(self) -> bool:
        """Verifica se o token está expirado."""
        return time.time() >= self.expires_at

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TokenData":
        """Cria uma instância de TokenData a partir de um dicionário."""
        return cls(
            access_token=data["access_token"], expires_at=float(data["expires_at"])
        )


class TokenServiceError(Exception):
    """Exceção customizada para erros do TokenService."""

    pass


class TokenService:
    """Serviço para gerenciamento de tokens de autenticação."""

    _instance = None
    CACHE_FILENAME = "token_cache.json"
    AUTH_URL = (
        "https://api.btgpactual.com/iaas-auth/api/v1/authorization/oauth2/accesstoken"
    )

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TokenService, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self._initialized = False
        self._token_data: Optional[TokenData] = None
        self._cache_path = Path(self.CACHE_FILENAME)

    def initialize(self) -> None:
        """Inicializa o serviço apenas uma vez."""
        if self._initialized:
            logger.debug("TokenService already initialized.")
            return

        logger.info("Initializing TokenService...")
        load_dotenv()

        auth_base64 = os.getenv("AUTH_BASE64")
        if not auth_base64:
            raise TokenServiceError("AUTH_BASE64 environment variable not set")

        self._request_id = str(uuid.uuid4())
        self._headers = self._build_headers(auth_base64)
        self._body = {"grant_type": "client_credentials"}
        self._token_data = self._load_cached_token()
        self._initialized = True

    def _build_headers(self, auth_base64: str) -> Dict[str, str]:
        """Constrói os headers para a requisição."""
        return {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "*/*",
            "Authorization": f"Basic {auth_base64}",
            "x-id-partner-request": self._request_id,
        }

    def get_token(self) -> str:
        """Retorna um token de acesso válido, utilizando cache se disponível."""
        if not self._initialized:
            self.initialize()

        if not self._token_data:
            self._token_data = self._load_cached_token()

        if self._token_data and not self._token_data.is_expired:
            return self._token_data.access_token

        return self._fetch_new_token()

    def _fetch_new_token(self) -> str:
        """Busca um novo token da API."""
        try:
            response = requests.post(
                self.AUTH_URL, headers=self._headers, data=self._body, timeout=30
            )

            logger.info(f"Token request status: {response.status_code}")

            if response.status_code != 200:
                raise TokenServiceError(
                    f"Failed to fetch access token: {response.status_code} - {response.text}"
                )

            token_data = self._process_response(response)
            self._save_token_to_cache(token_data)
            self._token_data = token_data

            return token_data.access_token

        except requests.RequestException as e:
            raise TokenServiceError(f"Request error: {str(e)}")

    def _process_response(self, response: requests.Response) -> TokenData:
        """Processa a resposta da API e extrai os dados do token."""
        access_token = response.headers.get("access_token")
        if not access_token:
            raise TokenServiceError("Access Token not found in response headers")

        expires_header = response.headers.get("expires")
        if not expires_header:
            raise TokenServiceError("Expiration time not found in response headers")

        try:
            expires_at = (
                datetime.strptime(expires_header, "%a, %d %b %Y %H:%M:%S %Z")
                .replace(tzinfo=timezone.utc)
                .timestamp()
            )

            return TokenData(access_token=access_token, expires_at=expires_at)

        except ValueError as e:
            raise TokenServiceError(f"Invalid expiration date format: {str(e)}")

    def _save_token_to_cache(self, token_data: TokenData) -> None:
        """Salva os dados do token em cache."""
        try:
            token_dict = {
                "access_token": token_data.access_token,
                "expires_at": token_data.expires_at,
            }

            self._cache_path.write_text(json.dumps(token_dict))
            logger.info("Token cached successfully")

        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to cache token: {str(e)}")

    def _load_cached_token(self) -> Optional[TokenData]:
        """Carrega o token do cache se existir e for válido."""
        try:
            if not self._cache_path.exists():
                return None

            data = json.loads(self._cache_path.read_text())
            token_data = TokenData.from_dict(data)

            if token_data.is_expired:
                logger.info("Cached token is expired")
                return None

            logger.info("Loaded valid token from cache")
            return token_data

        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load cached token: {str(e)}")
            return None
