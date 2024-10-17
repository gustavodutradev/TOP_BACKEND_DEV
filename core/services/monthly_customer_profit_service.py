# from core.services.config_service import ConfigService
# import requests
# from core.services.zip_service import ZipService


# class MonthlyCustomerProfitService:
#     """Classe para requisitar rentabilidade mensal do cliente."""

#     def __init__(self) -> None:
#         self.config_service = ConfigService()

#     def getProfitByPeriod(self):
#         """Requisita rentabilidade mensal do cliente."""
#         endpoint = "/api-partner-report-hub/api/v1/report/customer-profitability"
#         url = f"{self.config_service._base_url}{endpoint}"
#         period = {"referenceMonth": "x", "referenceYear": "y"}

#         try:
#             headers = self.config_service.get_headers()
#             response = requests.get(url, json=period, headers=headers)

#             if response.status_code == 202:
#                 print("Requisição aceita. Aguarde o webhook para processamento.")
#                 return True

#             print(f"Erro na requisição: {response.status_code} - {response.text}")
#             return None

#         except requests.RequestException as e:
#             print(f"Erro na requisição: {str(e)}")
#             return None

#     def process_csv_from_url(self, csv_url):
#         """Realiza o download do CSV zipado e extrai as informações"""
#         try:
#             zip_response = requests.get(csv_url)
#             if zip_response.status_code != 200:
#                 raise Exception(
#                     f"Erro ao baixar o arquivo ZIP: {zip_response.status_code}"
#                 )

#             zip_service = ZipService()

#             unziped_file = zip_service.unzip_csv_reader(zip_response)
#             return unziped_file

#         except requests.RequestException as e:
#             print(f"Erro na requisição: {str(e)}")
#             return None
