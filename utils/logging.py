import logging
import traceback
from flask import request, jsonify


class Logger:
    def __init__(self, app) -> None:
        self.app = app
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)

    def log_and_respond(self, event_name: str):
        try:
            # Captura o JSON da requisição e verifica se está no formato esperado
            data = request.get_json(force=True)

            # Se o JSON não estiver presente ou for inválido, retorna um erro 400
            if not data:
                self.app.logger.error(
                    f"Received Event {event_name} - No JSON payload found"
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

            # Verifica se 'data' é uma lista e pega o primeiro item, se aplicável
            if isinstance(data, list) and len(data) > 0:
                data = data[0]

                self.app.logger.debug(f"Payload Recebido: {data}")

            # Tenta obter a URL diretamente ou via campo 'response'
            url = data.get("result", {}).get(
                "url"
            )  # Acesso mais seguro ao JSON aninhado

            if not url:
                # Acessa com segurança a lista 'errors' e verifica se há pelo menos um erro
                errors = data.get("errors", [{}])
                error = errors[0] if isinstance(errors, list) and errors else {}

                # Coleta a mensagem e código de erro, com valores padrão
                message = error.get("message", "Unknown error")
                code = error.get("code", "Unknown code")

                # Log detalhado do evento e erro
                self.app.logger.warning(
                    f"Received Event {event_name} - URL not found in request data. "
                    f"Error Code: {code}, Message: {message}, Full Payload: {data}"
                )

                # Responde com o código de erro apropriado
                return jsonify({"status": code, "message": message}), 400

            # Loga o sucesso com a URL recebida
            self.logger.info(
                f"Received Event {event_name} - URL: {url}, Full Payload: {data}"
            )

            # Retorna sucesso quando o evento é processado corretamente
            return (
                jsonify(
                    {"status": "success", "message": "Event processed", "url": url}
                ),
                200,
            )

        except Exception as e:
            # Loga a exceção ocorrida durante o processamento da requisição, com traceback
            self.app.logger.error(f"Exception on {event_name} - {str(e)}")
            self.app.logger.error(traceback.format_exc())
            return jsonify({"status": "error", "message": "Internal server error"}), 500
