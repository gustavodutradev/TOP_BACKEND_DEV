from core.services.token_service import TokenService
from utils.logging_requests import Logger


class WebhookService:

    def __init__(self, app) -> None:
        self.app = app
        self.token_service = TokenService()
        self.register_routes()
        self.Logger = Logger(app)

    def register_routes(self):

        ## Rentabilidade Diária
        @self.app.route("/api/v1/daily-profit", methods=["POST"])
        def daily_profit():
            return self.Logger.log_and_respond("Daily Profit")

        @self.app.route("/api/v1/daily-profit-by-date", methods=["POST"])
        def daily_profit_by_date():
            return self.Logger.log_and_respond("Daily Profit by Date")

        ## Relatório STVM New NET Money
        @self.app.route("/api/v1/stvm", methods=["POST"])
        def stvm():
            return self.Logger.log_and_respond("STVM")

        ## Comissoes dos ultimos 4 dias
        @self.app.route("/api/v1/comissions", methods=["POST"])
        def commissions():
            return self.Logger.log_and_respond("Commissions")

        ## Rentabilidade Mensal
        @self.app.route("/api/v1/monthly-product-profit", methods=["POST"])
        def monthly_product_profit():
            return self.Logger.log_and_respond("Monthly Product Profit")

        ## Pré Operações
        @self.app.route("/api/v1/pre-operations", methods=["POST"])
        def pre_operations():
            return self.Logger.log_and_respond("Pre-Operations")

        ## Reservas de IPO
        @self.app.route("/api/v1/push-ofertas-ativas", methods=["POST"])
        def push_ofertas_ativas():
            return self.Logger.log_and_respond("Ofertas Ativas de IPO")

        @self.app.route("/api/v1/reservas-ofertas-ativas", methods=["POST"])
        def reservas_ofertas_ativas():
            return self.Logger.log_and_respond("Reservas de Ofertas Ativas")

        ## Operações
        @self.app.route("/api/v1/operations", methods=["POST"])
        def operations_all_accounts():
            return self.Logger.log_and_respond("Operations (All Accounts)")

        ## Relacionamento de Conta e Parceiro
        @self.app.route("/api/v1/relationship-accounts-advisors", methods=["POST"])
        def relationship_accounts_advisors():
            return self.Logger.log_and_respond("Relationship Accounts and Advisors")
