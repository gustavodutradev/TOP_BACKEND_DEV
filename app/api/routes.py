from flask import Blueprint, jsonify, request
from app.services.requests_service import RequestsService
from app.services.webhook_service import WebhookService

api_blueprint = Blueprint('api', __name__)

requests_service = RequestsService()
webhook_service = WebhookService()

# Rotas raiz e healthz
@api_blueprint.route('/')
def home():
    return jsonify({'message': 'API is running!'})

@api_blueprint.route('/healthz')
def health_check():
    return 'OK', 200

# Rotas para chamadas API BTG
@api_blueprint.route('/api/v1/get-suitability/<account_number>', methods=['GET'])
def get_suitability(account_number):
    suitability = requests_service.get_suitability(account_number)
    return jsonify(suitability)

@api_blueprint.route('/api/v1/get-registration-data/<account_number>', methods=['GET'])
def get_registration_data(account_number):
    registration_data = requests_service.get_registration_data(account_number)
    return jsonify(registration_data)

@api_blueprint.route('/api/v1/get-account-base', methods=['GET'])
def get_account_base():
    account_base = requests_service.get_account_base()
    return jsonify(account_base)

# # Rotas para Webhooks
# @api_blueprint.route('/api/v1/webhook-receiver', methods=['POST'])
# def webhook_receiver():
#     return webhook_service.handle_webhook(request)

# Você pode adicionar outras rotas para webhooks específicos se necessário
