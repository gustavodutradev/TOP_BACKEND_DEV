from flask import Flask
from services.webhook_service import WebhookService

app = Flask(__name__)

# Inicializa o serviço de webhook
webhook_service = WebhookService(app)

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)  # Executa o servidor localmente
