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
            data = request.get_json(force=True)

            # Verifica se o JSON está presente
            if not data:
                self.app.logger.error(f"Received Event {event_name} - No JSON payload found")
                return jsonify({"status": "Invalid request", "message": "No JSON payload found"}), 400

            # Verifica se 'data' é uma lista e usa o primeiro item se for aplicável
            if isinstance(data, list) and len(data) > 0:
                data = data[0]

            self.app.logger.debug(f"Payload Recebido: {data}")

            # Tenta obter a URL diretamente ou via campo 'result'
            url = data.get("result", {}).get("url")

            if not url:
                # Coleta a mensagem e código de erro (valores padrões usados caso não existam)
                errors = data.get("errors", [{}])
                error = errors[0] if isinstance(errors, list) and errors else {}
                message = error.get("message", "Unknown error")
                code = error.get("code", "Unknown code")

                # Log de advertência com detalhes do erro
                self.app.logger.warning(f"Received Event {event_name} - URL not found. Error Code: {code}, Message: {message}, Full Payload: {data}")

                # Retorna resposta de erro
                return jsonify({"status": code, "message": message}), 400

            # Log de sucesso
            self.logger.info(f"Received Event {event_name} - URL: {url}, Full Payload: {data}")

            # Responde com sucesso
            return jsonify({"status": "success", "message": "Event processed", "url": url}), 200

        except Exception as e:
            # Captura a exceção com detalhes do traceback
            self.app.logger.error(f"Exception on {event_name} - {str(e)}")
            self.app.logger.error(traceback.format_exc())
            
            # Retorna erro interno do servidor
            return jsonify({"status": "error", "message": "Internal server error"}), 500
