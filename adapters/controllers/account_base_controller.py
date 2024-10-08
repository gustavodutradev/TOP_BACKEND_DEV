from flask import jsonify
from core.services.account_base_service import AccountBaseService


class AccountBaseController:
    def __init__(self):
        self.account_base_service = AccountBaseService()

    def get_account_base(self):
        account_base = self.account_base_service.get_account_base()
        return jsonify(account_base)
