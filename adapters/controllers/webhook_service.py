from flask import request, jsonify
from core.services.token_service import TokenService
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
        url = data.get('url') or data.get('response', {}).get('url')

        if url is None:
            error = data.get('errors')
            message = error[0].get('message')
            code = error[0]
            self.app.logger.warning("Received Event Generic Webhook: URL not found in request data")
            return jsonify({"status": f'{code}', "message": f'{message}'}), 400

        self.logger.info(f"Received Event {event_name} - URL: {url}")
        return jsonify({"status": "success", "message": "Event processed", "url": url}), 200

    def register_routes(self):

        ## Relatórios Gerenciais
        @self.app.route('/api/v1/rg-tir-mensal-parceiro', methods=['POST'])
        def monthly_tir():
            return self.log_and_respond("RG - TIR_MENSAL")

        @self.app.route('/api/v1/rg-posicoes', methods=['POST'])
        def positions():
            return self.log_and_respond("RG - POSICOES")

        @self.app.route('/api/v1/rg-base-btg', methods=['POST'])
        def base_btg():
            return self.log_and_respond("RG - BASE BTG")

        @self.app.route('/api/v1/rg-nnm-gerencial', methods=['POST'])
        def nnm_gerencial():
            return self.log_and_respond("RG - NNM GERENCIAL")

        @self.app.route('/api/v1/rg-fundos', methods=['POST'])
        def fundos():
            return self.log_and_respond("RG - FUNDOS")
        
        @self.app.route('api/v1/rg-cra-cri', methods=['POST'])
        def cra_cri():
            return self.log_and_respond("RG - CRA/CRI")
        
        ## Rentabilidade Diária
        @self.app.route('/api/v1/daily-profit', methods=['POST'])
        def daily_profit():
            return self.log_and_respond("Daily Profit")
        
        @self.app.route('/api/v1/daily-profit-by-date', methods=['POST'])
        def daily_profit_by_date():
            return self.log_and_respond("Daily Profit by Date")

        ## Relatórios de Custódia
        @self.app.route('/api/v1/custody', methods=['POST'])
        def custody():
            return self.log_and_respond("Custody")
        
        @self.app.route('/api/v1/custody-by-date', methods=['POST'])
        def custody_by_date():
            return self.log_and_respond("Custody by Date")
        
        ## Relatório STVM New NET Money
        @self.app.route('/api/v1/stvm', methods=['POST'])
        def stvm():
            return self.log_and_respond("STVM")
 
        ## Comissoes dos ultimos 4 dias
        @self.app.route('/api/v1/comissions', methods=['POST'])
        def commissions():
            return self.log_and_respond("Commissions")
 
        ## Rentabilidade Mensal
        @self.app.route('/api/v1/monthly-customer-profit', methods=['POST'])
        def monthly_customer_profit():
            return self.log_and_respond("Monthly Customer Profit")
        
        @self.app.route('/api/v1/monthly-product-profit', methods=['POST'])
        def monthly_product_profit():
            return self.log_and_respond("Monthly Product Profit")

