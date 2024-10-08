from flask import jsonify
from core.services.suitability_service import SuitabilityService


class SuitabilityController:

    def __init__(self):
        self.suitability_service = SuitabilityService()

    def get_suitability(self, account_number):
        suitability = self.suitability_service.get_suitability(account_number)
        return jsonify(suitability)
