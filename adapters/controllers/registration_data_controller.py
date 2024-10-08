from flask import jsonify
from core.services.registration_data_service import RegistrationDataService


class RegistrationDataController:
    def __init__(self):
        self.registration_data_service = RegistrationDataService()

    def get_registration_data(self, account_number):
        registration_data = self.registration_data_service.get_registration_data(
            account_number
        )
        return jsonify(registration_data)
