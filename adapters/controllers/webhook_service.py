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

        # Verifica se 'data' é uma lista e pega o primeiro item
        if isinstance(data, list) and len(data) > 0:
            data = data[0]

        url = data.get("url") or data.get("response", {}).get("url")

        if url is None:
            # Verificação segura para acessar a lista 'errors', garantindo que sempre tenha um fallback
            errors = data.get("errors", [{}])
            if isinstance(errors, list) and len(errors) > 0:
                error = errors[0]
            else:
                error = {}

            # Coleta a mensagem e código do erro com valores padrão
            message = error.get("message", "Unknown error")
            code = error.get("code", "Unknown code")

            # Log detalhado quando o URL não é encontrado
            self.app.logger.warning(
                f"Received Event {event_name} - URL not found in request data. "
                f"Error Code: {code}, Message: {message}"
            )

            # Responde com o status e mensagem apropriados
            return jsonify({"status": f"{code}", "message": f"{message}"}), 400

        # Loga o evento com o URL encontrado
        self.logger.info(f"Received Event {event_name} - URL: {url}")

        # Retorna sucesso quando o evento é processado corretamente
        return (
            jsonify({"status": "success", "message": "Event processed", "url": url}),
            200,
        )

    def register_routes(self):

        ## Relatórios Gerenciais
        @self.app.route("/api/v1/rg-tir-mensal-parceiro", methods=["POST"])
        def monthly_tir():
            return self.log_and_respond("RG - TIR_MENSAL")

        @self.app.route("/api/v1/rg-posicoes", methods=["POST"])
        def positions():
            return self.log_and_respond("RG - POSICOES")

        @self.app.route("/api/v1/rg-base-btg", methods=["POST"])
        def base_btg():
            return self.log_and_respond("RG - BASE BTG")

        @self.app.route("/api/v1/rg-nnm-gerencial", methods=["POST"])
        def nnm_gerencial():
            return self.log_and_respond("RG - NNM GERENCIAL")

        @self.app.route("/api/v1/rg-fundos", methods=["POST"])
        def fundos():
            return self.log_and_respond("RG - FUNDOS")

        @self.app.route("/api/v1/rg-cra-cri", methods=["POST"])
        def cra_cri():
            return self.log_and_respond("RG - CRA/CRI")

        ## Rentabilidade Diária
        @self.app.route("/api/v1/daily-profit", methods=["POST"])
        def daily_profit():
            return self.log_and_respond("Daily Profit")

        @self.app.route("/api/v1/daily-profit-by-date", methods=["POST"])
        def daily_profit_by_date():
            return self.log_and_respond("Daily Profit by Date")

        ## Relatórios de Custódia
        @self.app.route("/api/v1/custody", methods=["POST"])
        def custody():
            return self.log_and_respond("Custody")

        @self.app.route("/api/v1/custody-by-date", methods=["POST"])
        def custody_by_date():
            return self.log_and_respond("Custody by Date")

        ## Relatório STVM New NET Money
        @self.app.route("/api/v1/stvm", methods=["POST"])
        def stvm():
            return self.log_and_respond("STVM")

        ## Comissoes dos ultimos 4 dias
        @self.app.route("/api/v1/comissions", methods=["POST"])
        def commissions():
            return self.log_and_respond("Commissions")

        ## Rentabilidade Mensal
        @self.app.route("/api/v1/monthly-customer-profit", methods=["POST"])
        def monthly_customer_profit():
            return self.log_and_respond("Monthly Customer Profit")

        @self.app.route("/api/v1/monthly-product-profit", methods=["POST"])
        def monthly_product_profit():
            return self.log_and_respond("Monthly Product Profit")

        ## Pré Operações
        @self.app.route("/api/v1/pre-operations", methods=["POST"])
        def pre_operations():
            return self.log_and_respond("Pre-Operations")

        ## Reservas de IPO
        @self.app.route("/api/v1/push-ofertas-ativas", methods=["POST"])
        def push_ofertas_ativas():
            return self.log_and_respond("Ofertas Ativas de IPO")

        @self.app.route("/api/v1/reservas-ofertas-ativas", methods=["POST"])
        def reservas_ofertas_ativas():
            return self.log_and_respond("Reservas de Ofertas Ativas")

        ## Ordens da Bolsa
        @self.app.route("/api/v1/orders", methods=["POST"])
        def orders():
            return self.log_and_respond("Orders")

        ## Operações
        @self.app.route("/api/v1/operations", methods=["POST"])
        def operations_all_accounts():
            return self.log_and_respond("Operations (All Accounts)")

        ## Relacionamento de Conta e Parceiro
        @self.app.route("/api/v1/relationship-accounts-advisors", methods=["POST"])
        def relationship_accounts_advisors():
            return self.log_and_respond("Relationship Accounts and Advisors")
