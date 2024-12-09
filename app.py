import os
import logging
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
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

# Load environment variables
load_dotenv()


class FlaskApp:
    def __init__(self):
        # Configure logging for production
        self._setup_logging()

        # Initialize Flask app
        self.app = Flask(__name__)

        # Configure CORS for security
        self._configure_cors()

        # Configure application settings
        self._configure_app()

        # Initialize controllers, routes, and schedulers
        self._init_controllers()
        self._init_routes()
        self._init_scheduler()

    def _setup_logging(self):
        """Configure logging for production environment"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),  # Console logging for Azure
            ],
        )
        self.logger = logging.getLogger(__name__)

    def _configure_cors(self):
        """Configure CORS with specific settings"""
        CORS(
            self.app,
            resources={
                r"/api/*": {
                    "origins": "*",  # Allow all origins for API routes
                    "methods": [
                        "GET",
                        "POST",
                        "PUT",
                        "DELETE",
                        "OPTIONS",
                    ],  # Allowed HTTP methods
                    "allow_headers": [
                        "Content-Type",
                        "Authorization",
                    ],  # Allowed headers
                }
            },
        )

    def _configure_app(self):
        """Configure Flask app for production"""
        # Set production configuration
        self.app.config["ENV"] = os.getenv("FLASK_ENV", "production")
        self.app.config["DEBUG"] = False
        self.app.config["TESTING"] = False
        self.app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "fallback_secret_key")

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
        """Initialize the task scheduler with error handling"""
        try:
            self.task_scheduler = PendingOrdersScheduler()
            self.custody_scheduler = CustodyScheduler()
            self.logger.info("Schedulers initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing schedulers: {e}")

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

        # Use Gunicorn for production
        from gunicorn.app.base import BaseApplication

        class GunicornApp(BaseApplication):
            def __init__(self, app, options=None):
                self.application = app
                self.options = options or {}
                super().__init__()

            def load_config(self):
                for key, value in self.options.items():
                    self.cfg.set(key.lower(), value)

            def load(self):
                return self.application

        options = {
            "bind": f"{host}:{port}",
            "workers": int(os.getenv("WEB_WORKERS", 3)),
            "worker_class": "gthread",
            "threads": int(os.getenv("WEB_THREADS", 2)),
            "worker_tmp_dir": "/dev/shm",
        }

        GunicornApp(self.app, options).run()


# WSGI application for production servers
application = FlaskApp().app

if __name__ == "__main__":
    app = FlaskApp()
    app.run()
