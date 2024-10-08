import uuid
from core.services.token_service import TokenService


class ConfigService(TokenService):
    def __init__(self) -> None:
        super().__init__()
        self._base_url = "https://api.btgpactual.com"
        self._uuid = uuid.uuid4()
        self._update_token()

    def _update_token(self):
        self._token = self.get_token()

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
