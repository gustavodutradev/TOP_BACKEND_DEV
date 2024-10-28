import logging
import traceback
from flask import request, jsonify


class Logger:
    def __init__(self, app) -> None:
        self.app = app
        self.setup_logging()

    def setup_logging(self):
        # Definindo um formato de log mais detalhado
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=log_format)
        self.logger = logging.getLogger(__name__)

    def log_and_respond(self, event_name: str):
        try:
            # Captura o JSON da requisição
            data = request.get_json(silent=True)

            # Verifica se o JSON está presente
            if not data:
                self.app.logger.error(
                    f"Received Event {event_name} - No JSON payload found",
                    extra=self._get_request_context(),
                )
                return (
                    jsonify(
                        {
                            "status": "Invalid request",
                            "message": "No JSON payload found",
                        }
                    ),
                    400,
                )

            # Se 'data' for uma lista, usa o primeiro item, caso aplicável
            if isinstance(data, list) and data:
                data = data[0]

            self.app.logger.debug(
                f"Payload Recebido: {data}", extra=self._get_request_context()
            )

            # Tenta obter a URL diretamente ou via campo 'result'
            url = data.get("result", {}).get("url")

            if not url:
                # Coleta mensagem e código de erro (valores padrões se ausentes)
                error = (data.get("errors") or [{}])[0]
                message = error.get("message", "Unknown error")
                code = error.get("code", "Unknown code")

                # Loga advertência com detalhes do erro
                self.app.logger.warning(
                    f"Received Event {event_name} - URL not found. "
                    f"Error Code: {code}, Message: {message}, Full Payload: {data}",
                    extra=self._get_request_context(),
                )

                # Retorna resposta de erro
                return jsonify({"status": code, "message": message}), 400

            # Loga sucesso com a URL encontrada
            self.logger.info(
                f"Received Event {event_name} - URL: {url}, Full Payload: {data}",
                extra=self._get_request_context(),
            )

            # Responde com sucesso
            return (
                jsonify(
                    {"status": "success", "message": "Event processed", "url": url}
                ),
                200,
            )

        except Exception as e:
            # Loga a exceção com detalhes do traceback
            self.app.logger.error(
                f"Exception on {event_name} - {str(e)}",
                extra=self._get_request_context(),
            )
            self.app.logger.error(traceback.format_exc())

            # Retorna erro interno do servidor
            return jsonify({"status": "error", "message": "Internal server error"}), 500

    def _get_request_context(self):
        """Obtém detalhes do contexto da requisição para enriquecer os logs."""
        return {
            "clientip": request.remote_addr,
            "method": request.method,
            "url": request.url,
        }
