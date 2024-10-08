from core.services.recommended_equities_service import RecommendedEquitiesService
from flask import jsonify


class RecommendedEquitiesController:
    def __init__(self):
        self.recommended_equities_service = RecommendedEquitiesService()

    def get_recommended_equities(self):
        recommended_equities = (
            self.recommended_equities_service.get_recommended_equities()
        )
        return jsonify(recommended_equities)
