import json
import logging

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MapAdvisorInfo:
    def __init__(self):
        # Carrega os dados de contas e assessores a partir de arquivos JSON
        self.account_data = self.load_json("resources/data/account_advisors_data.json")
        self.advisor_data = self.load_json("resources/data/advisors_data.json")

        # Verifica se os dados foram carregados corretamente
        if self.account_data and self.advisor_data:
            logger.info("Dados de contas e assessores carregados com sucesso.")
            logger.debug(f"Assessores: {self.advisor_data}")
        else:
            logger.error("Erro ao carregar os dados de contas e assessores.")

    @staticmethod
    def load_json(filepath):
        """Carrega dados de um arquivo JSON e lida com possíveis erros."""
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Erro: Arquivo {filepath} não encontrado.")
            return []
        except json.JSONDecodeError:
            print(f"Erro: Falha ao decodificar o arquivo {filepath}.")
            return []

    def map_accounts_to_advisors(self, account_number):
        # Criar um dicionário de assessores com base no código CGE do assessor (para fácil busca)
        advisor_dict = {
            advisor["advisorCgeCode"]: advisor for advisor in self.advisor_data
        }

        # Iterar sobre as contas para encontrar a conta correspondente ao número fornecido
        for key in self.account_data:
            if key["account"] == account_number:
                # Encontrou a conta, agora associamos o assessor
                assessor_cge_code = key["sgCGE"]

                # Se encontrar o assessor correspondente, retornamos as informações
                if assessor_cge_code in advisor_dict:
                    advisor = advisor_dict[assessor_cge_code]
                    logger.info(f"Encontrado assessor: {advisor['advisorName']}")
                    return (
                        key["clientName"],
                        advisor["advisorName"],
                        advisor["email"],
                        advisor["phone"],
                    )

                else:
                    logger.error(
                        f"Assessor com código CGE {assessor_cge_code} não encontrado."
                    )
                    return key["clientName"], key["nome_assessor"], None, None

        # Caso o número da conta não seja encontrado, retorne valores padrão
        logger.error(f"Conta {account_number} não encontrada.")
        return None, None, None, None
