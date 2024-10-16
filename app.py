from flask import Flask
from adapters.controllers.webhook_service import WebhookService
from adapters.controllers.suitability_controller import SuitabilityController
from adapters.controllers.registration_data_controller import RegistrationDataController
from adapters.controllers.account_base_controller import AccountBaseController
from adapters.controllers.debentures_controller import DebenturesController
from adapters.controllers.stock_orders_controller import StockOrdersController
from adapters.controllers.recommended_equities_controller import (
    RecommendedEquitiesController,
)
from scheduler.pending_orders_scheduler import PendingOrdersScheduler
import os

app = Flask(__name__)

# Inicializa o serviço de webhook
webhook_service = WebhookService(app)

suitability_controller = SuitabilityController()
registration_data_controller = RegistrationDataController()
account_base_controller = AccountBaseController()
debentures_controller = DebenturesController()
recommended_equities_controller = RecommendedEquitiesController()
stock_order_controller = StockOrdersController(app)

task_scheduler = PendingOrdersScheduler()


@app.route("/healthz")
def health_check():
    return "OK", 200


@app.route("/")
def home():
    return "API is running!"


@app.route("/api/v1/get-suitability/<account_number>", methods=["GET"])
def get_suitability(account_number):
    return suitability_controller.get_suitability(account_number)


@app.route("/api/v1/get-registration-data/<account_number>", methods=["GET"])
def get_registration_data(account_number):
    return registration_data_controller.get_registration_data(account_number)


@app.route("/api/v1/get-holder-name/<account_number>", methods=["GET"])
def get_holder_name(account_number):
    return registration_data_controller.get_holder_name(account_number)


@app.route("/api/v1/get-account-base", methods=["GET"])
def get_account_base():
    return account_base_controller.get_account_base()


@app.route("/api/v1/get-anbima-debentures/<date>", methods=["GET"])
def anbima_debentures(date):
    return debentures_controller.get_anbima_debentures(date)


@app.route("/api/v1/get-recommended-equities/<date>", methods=["GET"])
def get_recommended_equities(date):
    return recommended_equities_controller.get_recommended_equities(date)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
