from flask import jsonify
from core.services.registration_data_service import RegistrationDataService


class RegistrationDataController:
    def __init__(self):
        self.registration_data_service = RegistrationDataService()

    def get_registration_data(self, account_number):
        """Retorna todos os dados da conta."""
        registration_data = self.registration_data_service.get_registration_data(
            account_number
        )
        return jsonify(registration_data)

    def get_holder_name(self, account_number):
        """Retorna apenas o nome do titular da conta."""
        holder_name = self.registration_data_service.get_holder_name(account_number)
        return jsonify({"holder_name": holder_name})
