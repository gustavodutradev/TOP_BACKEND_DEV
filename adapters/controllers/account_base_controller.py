from flask import jsonify
from core.services.account_base_service import AccountBaseService
from database.connection import get_db  # Assumindo que você tenha um método para obter a sessão do DB

class AccountBaseController:
    def __init__(self):
        self.account_base_service = AccountBaseService()

    def get_account_base(self):
        # Obtém a sessão do banco de dados
        db = next(get_db())

        # Chama o serviço que retorna e persiste os dados
        account_base = self.account_base_service.get_account_base(db)
        return jsonify(account_base)
