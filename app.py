from flask import Flask
from typing import Tuple

from adapters.controllers import (
    SuitabilityController,
    RegistrationDataController,
    AccountBaseController,
    AnbimaDebenturesController,
    StockOrdersController,
    RecommendedEquitiesController,
    MonthlyCustomerProfitController,
    BaseBTGController,
    PositionReportController,
    MonthlyTIRController,
    CraCriController,
    FixedIncomeController,
    RFDebenturesController,
    GovBondController,
    CompromissadasController,
    CommissionsController,
    ClosedCommissionsController,
    NNMController,
    FundsController,
    OperationsController,
    PreOperationsController,
    CustodyByDateController,
    CustodyController,
    LifeInsuranceController,
    PositionsByAccountController,
    PositionsByPartnerController,
    ExchangeController,
    RelationshipController,
    BankingController,
    CreditCardController,
    MonthlyNNMController,
)
from scheduler.pending_orders_scheduler import PendingOrdersScheduler
from scheduler.custody_scheduler import CustodyScheduler


class FlaskApp:
    def __init__(self):
        self.app = Flask(__name__)
        self._init_controllers()
        self._init_routes()
        self._init_scheduler()

    def _init_controllers(self) -> None:
        """Initialize all controllers"""
        self.controllers = {
            "suitability": SuitabilityController(self.app),
            "registration": RegistrationDataController(self.app),
            "account": AccountBaseController(),
            "debentures": AnbimaDebenturesController(self.app),
            "recommended_equities": RecommendedEquitiesController(),
            "stock_orders": StockOrdersController(self.app),
            "monthly_profit": MonthlyCustomerProfitController(self.app),
            "base_btg": BaseBTGController(self.app),
            "positions": PositionReportController(self.app),
            "monthly_tir": MonthlyTIRController(self.app),
            "cra_cri": CraCriController(self.app),
            "fixed_income": FixedIncomeController(self.app),
            "rf_debentures": RFDebenturesController(self.app),
            "gov_bond": GovBondController(self.app),
            "compromissadas": CompromissadasController(self.app),
            "commissions": CommissionsController(self.app),
            "closed_commissions": ClosedCommissionsController(self.app),
            "nnm": NNMController(self.app),
            "monthly_nnm": MonthlyNNMController(self.app),
            "funds": FundsController(self.app),
            "exchange": ExchangeController(self.app),
            "operations": OperationsController(self.app),
            "pre_operations": PreOperationsController(self.app),
            "custody_by_date": CustodyByDateController(self.app),
            "custody": CustodyController(self.app),
            "life_insurance": LifeInsuranceController(self.app),
            "positions_by_account": PositionsByAccountController(self.app),
            "positions_by_partner": PositionsByPartnerController(self.app),
            "relationship": RelationshipController(self.app),
            "banking": BankingController(self.app),
            "credit_card": CreditCardController(self.app),
        }

    def _init_scheduler(self) -> None:
        """Initialize the task scheduler"""
        self.task_scheduler = PendingOrdersScheduler()
        self.custody_scheduler = CustodyScheduler()

    def _init_routes(self) -> None:
        """Initialize all routes"""
        # Health check routes
        self.app.add_url_rule("/healthz", "health_check", self.health_check)
        self.app.add_url_rule("/", "home", self.home)

        # API routes
        self.app.add_url_rule(
            "/api/v1/get-account-base",
            "get_account_base",
            self.get_account_base,
            methods=["GET"],
        )
        self.app.add_url_rule(
            "/api/v1/get-recommended-equities/<date>",
            "get_recommended_equities",
            self.get_recommended_equities,
            methods=["GET"],
        )

    def health_check(self) -> Tuple[str, int]:
        """Health check endpoint"""
        return "OK", 200

    def home(self) -> str:
        """Home endpoint"""
        return "API is running!"

    def get_account_base(self):
        """Get account base endpoint"""
        return self.controllers["account"].get_account_base()

    def get_recommended_equities(self, date: str):
        """Get recommended equities endpoint"""
        return self.controllers["recommended_equities"].get_recommended_equities(date)

    def run(self, host: str = "0.0.0.0", port: int = None) -> None:
        """Run the Flask application"""
        if port is None:
            port = int(os.environ.get("PORT", 5000))
        self.app.run(host=host, port=port)


if __name__ == "__main__":
    import os

    app = FlaskApp()
    app.run()
else:
    # Expose WSGI callable for gunicorn
    application = FlaskApp().app

