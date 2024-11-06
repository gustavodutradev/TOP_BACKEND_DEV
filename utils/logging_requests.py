import logging
import traceback
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple
from flask import Request, request, jsonify


@dataclass
class RequestContext:
    """Classe para armazenar o contexto da requisição."""

    clientip: str
    method: str
    url: str

    @classmethod
    def from_request(cls, request: Request) -> "RequestContext":
        return cls(clientip=request.remote_addr, method=request.method, url=request.url)


class Logger:
    def __init__(self, app) -> None:
        self.app = app
        self.setup_logging()

    def setup_logging(self) -> None:
        """Configura o logger com formato detalhado."""
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=log_format)
        self.logger = logging.getLogger(__name__)

    def extract_url(self, data: Dict[str, Any]) -> Optional[str]:
        """Extrai a URL do payload, procurando em diferentes locais possíveis."""
        return (
            data.get("result", {}).get("url", "")
            or data.get("response", {}).get("url", "")
            or data.get("url", "")
        )

    def extract_error_info(self, data: Dict[str, Any]) -> Tuple[str, str]:
        """Extrai informações de erro do payload."""
        error = (data.get("errors") or [{}])[0]
        return (
            error.get("message", "Unknown error"),
            error.get("code", "Unknown code"),
        )

    def process_payload(
        self, data: Dict[str, Any], event_name: str
    ) -> Tuple[Dict[str, Any], int]:
        """Processa o payload e retorna a resposta apropriada."""
        if isinstance(data, list) and data:
            data = data[0]

        self.app.logger.debug(
            f"Payload Recebido: {data}",
            extra=RequestContext.from_request(request).__dict__,
        )

        url = self.extract_url(data)
        if not url:
            message, code = self.extract_error_info(data)
            self.app.logger.warning(
                f"Received Event {event_name} - URL not found. "
                f"Error Code: {code}, Message: {message}, Full Payload: {data}",
                extra=RequestContext.from_request(request).__dict__,
            )
            return {"status": code, "message": message}, 400

        self.logger.info(
            f"Received Event {event_name} - URL: {url}, Full Payload: {data}",
            extra=RequestContext.from_request(request).__dict__,
        )

        return {"status": "success", "message": "Event processed", "url": url}, 200

    def log_and_respond(self, event_name: str) -> Tuple[Dict[str, Any], int]:
        try:
            data = request.get_json(silent=True)
            if data:
                response_data, status_code = self.process_payload(data, event_name)
                return jsonify(response_data), status_code
            else:
                self.app.logger.info(
                    f"Received Event {event_name}",
                    extra=RequestContext.from_request(request).__dict__,
                )
                return jsonify({"status": "success", "message": event_name}), 200
        except Exception as e:
            self.app.logger.error(
                f"Exception on {event_name} - {str(e)}",
                extra=RequestContext.from_request(request).__dict__,
            )
            self.app.logger.error(traceback.format_exc())
            return jsonify({"status": "error", "message": "Internal server error"}), 500
