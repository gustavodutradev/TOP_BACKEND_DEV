from flask import request, jsonify
from services.token_service import TokenService
import logging

class WebhookService:

    def __init__(self, app) -> None:
        self.app = app
        self.token_service = TokenService()
        self.register_routes()
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def log_and_respond(self, event_name: str):
        data = request.json
        url = data.get('response', {}).get('URL')

        if url:
            self.logger.info("Received Event %s: URL - %s", event_name, url)
            return jsonify({"status": "success", "message": "Event processed", "url": url}), 200
        else:
            self.logger.warning("Received Event %s: URL not found in request data", event_name)
            return jsonify({"status": "failure", "message": "URL not found"}), 400

        return jsonify({"status": "success", "message": f"Event {event_name} processed"}), 200

    def register_routes(self):
        @self.app.route('/api/v1/rg-tir-mensal-parceiro', methods=['POST'])
        def webhook_monthly_tir():
            return self.log_and_respond("RG - TIR_MENSAL")

        @self.app.route('/api/v1/rg-posicoes', methods=['POST'])
        def webhook_positions():
            return self.log_and_respond("RG - POSICOES")

        @self.app.route('/api/v1/rg-base-btg', methods=['POST'])
        def webhook_base_btg():
            return self.log_and_respond("RG - BASE BTG")

        @self.app.route('/api/v1/rg-nnm-gerencial', methods=['POST'])
        def webhook_nnm_gerencial():
            return self.log_and_respond("RG - NNM GERENCIAL")

        @self.app.route('/api/v1/rg-fundos', methods=['POST'])
        def webhook_fundos():
            return self.log_and_respond("RG - FUNDOS")
        
        @self.app.route('/api/v1/webhook-receiver', methods=['POST'])
        def webhook_receiver():
            return self.log_and_respond("Generic Webhook")
        
        @self.app.route('/healthz')
        def health_check():
            return 'OK', 200
        
        @self.app.route('/')
        def home():
            return "API is running!"
