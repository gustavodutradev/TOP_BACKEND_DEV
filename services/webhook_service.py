from flask import request, jsonify
from services.token_service import TokenService

class WebhookService:

    def __init__(self, app) -> None:
        self.app = app
        self.token_service = TokenService()
        self.register_routes()

    def register_routes(self):
        @self.app.route('/api/v1/rg-tir-mensal-parceiro', methods=['POST'])
        def webhook_event1():
            data = request.json
            print("Received Event RG - TIR_MENSAL:", data)
            return jsonify({"status": "success", "message": "Event TIR_MENSAL processed"}), 200

        @self.app.route('/api/v1/rg-posicoes', methods=['POST'])
        def webhook_event2():
            data = request.json
            print("Received Event RG - Posições:", data)
            return jsonify({"status": "success", "message": "Event Posicoes processed"}), 200

        @self.app.route('/api/v1/rg-base-btg', methods=['POST'])
        def webhook_event3():
            data = request.json
            print("Received Event RG - BASE_BTG:", data)
            return jsonify({"status": "success", "message": "Event BASE BTG processed"}), 200

        @self.app.route('/api/v1/rg-nnm-gerencial', methods=['POST'])
        def webhook_event4():
            data = request.json
            print("Received Event RG - NNM Gerencial:", data)
            return jsonify({"status": "success", "message": "Event NNM Gerencial processed"}), 200

        @self.app.route('/api/v1/rg-fundos', methods=['POST'])
        def webhook_event5():
            data = request.json
            print("Received Event RG - Fundos:", data)
            return jsonify({"status": "success", "message": "Event Fundos processed"}), 200
        
        @self.app.route('/api/v1/webhook-receiver', methods=['POST'])
        def webhook_receiver():
            data = request.json
            print("Received Event:", data)
            return jsonify({"status": "success", "message": "Event processed"}), 200
        
        @self.app.route('/healthz')
        def health_check():
            return 'OK', 200
