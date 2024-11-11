import requests
import io
import pandas as pd
import logging
import json
from datetime import datetime
from pathlib import Path

# import os

from core.services.config_service import ConfigService
from core.services.email_service import EmailService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CommissionsService:
    """Classe para requisitar relatório de Comissões dos Assessores"""

    def __init__(self) -> None:
        self.config_service = ConfigService()
        self.email_service = EmailService()
        self.unprocessed_accounts = set()
        self.processed_data = {}
        self.account_base_data = self.load_json(
            "resources/data/account_advisors_data.json"
        )
        self.advisors_data = self.load_json("resources/data/advisors_data.json")

    def get_commissions_report(self):
        """Requisita relatório gerencial de Comissões"""
        endpoint = "/api-rm-reports/api/v1/rm-reports/commission"
        url = f"{self.config_service.base_url}{endpoint}"

        try:
            headers = self.config_service.get_headers()
            response = requests.get(url, headers=headers)

            if response.status_code == 202:
                logger.info("Requisição aceita. Aguarde o webhook para processamento.")
                return True

            logger.error(
                f"Erro na requisição: {response.status_code} - {response.text}"
            )
            return None

        except requests.RequestException as e:
            logger.error(f"Erro na requisição: {str(e)}")
            return None

    @staticmethod
    def load_json(path):
        """Carrega dados de um arquivo JSON e lida com possíveis erros."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        except FileNotFoundError:
            logger.error(f"Erro: O arquivo {path} não existe.")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar o arquivo JSON: {e}")
            raise

    def process_csv_from_url(self, csv_url):
        """Realiza o download do CSV e extrai as informações"""
        try:
            csv_response = requests.get(csv_url)
            if csv_response.status_code != 200:
                raise Exception(
                    f"Erro ao baixar o arquivo CSV: {csv_response.status_code}"
                )

            csv_content = io.StringIO(csv_response.text)
            data = pd.read_csv(csv_content, delimiter=",")
            self.process_commissions(data)
            return data

        except requests.RequestException as e:
            logger.error(f"Erro na requisição: {str(e)}")
            return None

    def get_advisor_info(self, account_number):
        """
        Dado um número de conta, retorna as informações do assessor responsável.
        """
        account_number = str(account_number)

        try:
            # Encontra os dados da conta no primeiro JSON
            account_info = next(
                (
                    data
                    for data in self.account_base_data
                    if str(data["account"]) == account_number
                ),
                None,
            )

            if not account_info:
                self.unprocessed_accounts.add(account_number)
                return None

            # Encontra os dados do assessor no segundo JSON
            advisor_info = next(
                (
                    data
                    for data in self.advisors_data
                    if data["advisorCgeCode"] == account_info["sgCGE"]
                ),
                None,
            )

            if not advisor_info:
                self.unprocessed_accounts.add(account_number)
                logger.warning(
                    f"Assessor não encontrado para CGE: {account_info['sgCGE']}"
                )
                return None

            return {
                "advisorName": advisor_info["advisorName"],
                "advisorCgeCode": advisor_info["advisorCgeCode"],
                "email": advisor_info["email"],
            }

        except Exception as e:
            logger.error(f"Erro ao buscar informações do assessor: {e}")
            self.unprocessed_accounts.add(account_number)
            return None

    def process_commissions(self, commissions_data):
        """
        Processa os dados de comissões e organiza por assessor.
        """
        try:
            total_records = len(commissions_data)
            processed_records = 0

            # Itera sobre cada linha do DataFrame de comissões
            for _, row in commissions_data.iterrows():
                advisor_info = self.get_advisor_info(row["nr_conta"])

                if advisor_info:
                    advisor_key = f"{advisor_info['advisorName']}_{advisor_info['advisorCgeCode']}"

                    # Inicializa a lista de dados do assessor se não existir
                    if advisor_key not in self.processed_data:
                        self.processed_data[advisor_key] = []

                    # Adiciona os dados da comissão para o assessor
                    self.processed_data[advisor_key].append(row.to_dict())
                    processed_records += 1

            logger.info(
                f"Processamento concluído para {len(self.processed_data)} assessores"
            )
            logger.info(
                f"Registros processados: {processed_records} de {total_records}"
            )
            logger.info(f"Contas não processadas: {len(self.unprocessed_accounts)}")

        except Exception as e:
            logger.error(f"Erro ao processar comissões: {e}")
            raise

    def send_commissions_report(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_dir = f"relatorios_comissoes/relatorio_{timestamp}"
            Path(report_dir).mkdir(parents=True, exist_ok=True)

            attachments = []

            # Gera os arquivos Excel e adiciona à lista de anexos
            for advisor_key, data in self.processed_data.items():
                if not data:
                    continue

                df = pd.DataFrame(data)
                df = df.sort_values(["nr_conta", "dt_referencia"])
                excel_file = f"{report_dir}/{advisor_key}.xlsx"
                df.to_excel(excel_file, index=False, engine="openpyxl")
                attachments.append(excel_file)

            # Gera o arquivo de contas não processadas
            if self.unprocessed_accounts:
                unprocessed_df = pd.DataFrame(
                    list(self.unprocessed_accounts), columns=["Conta"]
                )
                unprocessed_file = f"{report_dir}/contas_nao_processadas.xlsx"
                unprocessed_df.to_excel(
                    unprocessed_file, index=False, engine="openpyxl"
                )
                attachments.append(unprocessed_file)

            # Cria o corpo do email em formato HTML
            html_content = f"""
            <html>
            <body>
                <h2>Relatório de Comissões</h2>
                <p>Anexamos os relatórios de comissões referentes ao período.</p>
                <h3>Contas Não Processadas:</h3>
                <p>As seguintes contas não puderam ser processadas:</p>
                <ul>
                    {''.join(f'<li>{conta}</li>' for conta in self.unprocessed_accounts)}
                </ul>
            </body>
            </html>
            """
            # to_emails = os.getenv("NOTIFY_EMAIL")

            # Envia o email com os arquivos anexados
            self.email_service.send_email(
                to_emails="gustavodutra@topinvgroup.com",
                subject="Relatório de Comissões",
                content=html_content,
                is_html=True,
                attachments=attachments,
            )

            logger.info(f"Processamento concluído. Relatório enviado por e-mail.")
            return report_dir

        except Exception as e:
            logger.error(f"Erro ao enviar relatórios por e-mail: {e}")
            raise
