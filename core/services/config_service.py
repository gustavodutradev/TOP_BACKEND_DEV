import uuid
from core.services.token_service import TokenService


class ConfigService:
    _instance = None  # Singleton

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ConfigService, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.token_service = TokenService()  # Obtém a instância singleton
        self._base_url = "https://api.btgpactual.com"
        self._uuid = uuid.uuid4()
        self._update_token()

    def _update_token(self):
        self._token = self.token_service.get_token()

        if not self._token:
            raise Exception("Token de acesso não disponível.")

        self._headers = {
            "Content-Type": "application/json",
            "Accept": "*/*",
            "x-id-partner-request": str(self._uuid),
            "access_token": self._token,
        }

    def get_headers(self):
        self._update_token()
        return self._headers
