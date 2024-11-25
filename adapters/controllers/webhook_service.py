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

        ## Rentabilidade Mensal
        @self.app.route("/api/v1/monthly-product-profit", methods=["POST"])
        def monthly_product_profit():
            return self.Logger.log_and_respond("Monthly Product Profit")

        ## Reservas de IPO
        @self.app.route("/api/v1/push-ofertas-ativas", methods=["POST"])
        def push_ofertas_ativas():
            return self.Logger.log_and_respond("Ofertas Ativas de IPO")

        @self.app.route("/api/v1/reservas-ofertas-ativas", methods=["POST"])
        def reservas_ofertas_ativas():
            return self.Logger.log_and_respond("Reservas de Ofertas Ativas")
