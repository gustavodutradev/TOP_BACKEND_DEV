import json
import requests
from core.services.config_service import ConfigService
from sqlalchemy.orm import Session
from database.models import Conta

class AccountBaseService:
    def __init__(self):
        self.config_service = ConfigService()

    def get_account_base(self, db: Session):
        endpoint = "/api-account-base/api/v1/account-base/accounts"
        url = f"{self.config_service.base_url}{endpoint}"

        print(url)

        try:
            headers = self.config_service.get_headers()

            response = requests.get(url, headers=headers)

            # Logando status code e response text
            print(f"Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")

            # Verifica se a resposta não é 200
            if response.status_code != 200:
                print(
                    f"Erro ao acessar Base de Contas: {response.status_code} - {response.text}"
                )
                return {"error": "Falha ao acessar o endpoint."}

            # Tentando decodificar a resposta JSON
            response_data = response.json()

            # Verifica se a resposta JSON é válida
            if response_data is None or not isinstance(response_data, dict):
                print("Resposta JSON é nula ou inválida.")
                return {"error": "Nenhum dado retornado."}

            # Processa as contas e salva no banco de dados
            self.save_accounts(db, response_data["accounts"])

            # Retorna a resposta correta
            return response_data

        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição: {str(e)}")
            return {"error": str(e)}
        except json.JSONDecodeError:
            print("Erro ao decodificar JSON da resposta.")
            return {"error": "Erro ao decodificar a resposta da API."}

    def save_accounts(self, db: Session, accounts: list):
        # Salva as contas no banco de dados
        for account in accounts:
            conta = Conta(account_number=account["accountNumber"], type_fund=account["typeFund"])
            db.add(conta)  # Adiciona a conta na sessão
        db.commit()  # Confirma as alterações no banco de dados
