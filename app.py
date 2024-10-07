from flask import Flask, jsonify
from adapters.controllers.webhook_service import WebhookService
from core.services.requests_service import RequestsService
import os

app = Flask(__name__)

# Inicializa o serviço de webhook
webhook_service = WebhookService(app)

# Inicializa o serviço de requests
requests_service = RequestsService()

@app.route('/healthz')
def health_check():
    return 'OK', 200

@app.route('/')
def home():
    return "API is running!"

@app.route('/api/v1/get-suitability/<account_number>', methods=['GET'])
def get_suitability(account_number):
    suitability = requests_service.get_suitability(account_number)
    return jsonify(suitability)

@app.route('/api/v1/get-registration-data/<account_number>', methods=['GET'])
def get_registration_data(account_number):
    registration_data = requests_service.get_registration_data(account_number)
    return jsonify(registration_data)

@app.route('/api/v1/get-account-base', methods=['GET'])
def get_account_base():
    account_base = requests_service.get_account_base()
    return jsonify(account_base)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

