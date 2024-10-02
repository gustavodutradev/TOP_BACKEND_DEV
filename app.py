from flask import Flask
from services.webhook_service import WebhookService
import os

app = Flask(__name__)

# Inicializa o serviço de webhook
webhook_service = WebhookService(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

