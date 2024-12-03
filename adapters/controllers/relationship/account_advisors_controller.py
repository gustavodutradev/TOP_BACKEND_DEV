from flask import request
from core.services.relationship.account_advisors_service import RelationshipService
from utils.logging_requests import Logger
from typing import Dict, Tuple, Any
import traceback
from http import HTTPStatus


class RelationshipController:
    def __init__(self, app):
        self.relationship_service = RelationshipService()
        self.app = app
        self.logger = Logger(app)
        self.register_routes()

    def register_routes(self) -> None:
        """Register the API routes for the controller."""
        self.app.add_url_rule(
            "/api/v1/relationship-accounts-advisors",
            "relationship_accounts_advisors_handler",
            self.handler,
            methods=["POST"],
        )

    def handler(self) -> Tuple[Dict[str, Any], int]:
        """
        Handle the initial request and process webhooks.
        
        Returns:
            Tuple containing response data and HTTP status code
        """
        try:
            if not request.is_json:
                return self._handle_initial_request()

            data = request.get_json(silent=True)
            if data and "response" in data:
                return self._process_webhook(data)

            return self._handle_initial_request()

        except Exception as e:
            return self._handle_error(e)

    def _handle_initial_request(self) -> Tuple[Dict[str, Any], int]:
        """
        Handle the initial linked accounts request.
        
        Returns:
            Tuple containing response data and HTTP status code
        """
        self.logger.log_and_respond("Starting linked accounts request.")

        if not self.relationship_service.get_account_advisors_relationship():
            return {
                "error": "Failed to initiate linked accounts request."
            }, HTTPStatus.INTERNAL_SERVER_ERROR

        return {
            "message": "Request accepted. Awaiting webhook processing."
        }, HTTPStatus.ACCEPTED

    def _process_webhook(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Process the webhook payload from the API.
        
        Args:
            data: The webhook payload data
        
        Returns:
            Tuple containing response data and HTTP status code
        """
        self.logger.log_and_respond("Webhook received.")

        csv_url = self._extract_csv_url(data)
        if not csv_url:
            self.logger.logger.error("CSV URL not found in payload.")
            return {"error": "CSV URL not found."}, HTTPStatus.BAD_REQUEST

        csv_data = self.relationship_service.process_csv_from_url(csv_url)
        if csv_data is None:
            self.logger.logger.info("No linked accounts found.")
            return {
                "message": "No linked accounts found."
            }, HTTPStatus.NO_CONTENT

        self.logger.logger.info("Linked accounts processed successfully.")
        return {"message": "Linked accounts processed successfully."}, HTTPStatus.OK

    def _extract_csv_url(self, data: Dict[str, Any]) -> str:
        """
        Extract CSV URL from webhook payload.
        
        Args:
            data: The webhook payload data
        
        Returns:
            The CSV URL if found, empty string otherwise
        """
        return data.get("response", {}).get("url", "")

    def _handle_error(self, error: Exception) -> Tuple[Dict[str, Any], int]:
        """
        Handle and log any exceptions that occur during processing.
        
        Args:
            error: The exception that occurred
        
        Returns:
            Tuple containing error response and HTTP status code
        """
        self.logger.logger.error(f"Request error: {str(error)}")
        self.logger.logger.error(traceback.format_exc())
        return {"error": "Internal server error"}, HTTPStatus.INTERNAL_SERVER_ERROR