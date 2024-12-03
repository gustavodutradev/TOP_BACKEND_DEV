from core.services.config_service import ConfigService
import requests
from core.services.zip_service import ZipService
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RelationshipService:
    """Service for requesting and processing account-advisor relationships."""

    def __init__(self) -> None:
        self.config_service = ConfigService()

    def get_account_advisors_relationship(self) -> Optional[bool]:
        """
        Request linked accounts from the client.
        
        Returns:
            bool: True if request is successful, None otherwise
        """
        endpoint = "/iaas-account-advisor/api/v1/advisor/link/account"
        url = f"{self.config_service.base_url}{endpoint}"

        try:
            headers = self.config_service.get_headers()
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                logger.info("Request accepted. Awaiting webhook processing.")
                return True

            logger.error(f"Request error: {response.status_code} - {response.text}")
            return None

        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return None

    def process_csv_from_url(self, csv_url: str) -> Optional[bool]:
        """
        Download zipped CSV and extract information.
        
        Args:
            csv_url (str): URL of the zipped CSV file
        
        Returns:
            Optional[bool]: True if processing is successful, None otherwise
        """
        try:
            zip_response = requests.get(csv_url)
            if zip_response.status_code != 200:
                raise Exception(f"Error downloading ZIP file: {zip_response.status_code}")

            zip_service = ZipService()
            unzipped_file = zip_service.unzip_csv_reader(zip_response)

            relationship_list = []
            for reader in unzipped_file:
                for row in reader:
                    account_info = {
                        "customer_account": row.get("account"),
                        "advisor_cge": row.get("sgCGE"),
                    }
                    relationship_list.append(account_info)
            logger.info(f"Account list: {relationship_list}")
            return relationship_list

        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return None