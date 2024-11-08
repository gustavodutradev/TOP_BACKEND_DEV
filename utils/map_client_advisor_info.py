import json

class MapAdvisorInfo:
    def __init__(self):
        # Carrega os dados de contas e assessores a partir de arquivos JSON
        self.account_data = self.load_json("resources/data/account_advisors_data.json")
        self.advisor_data = self.load_json("resources/data/advisors_data.json")

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
        advisor_dict = {advisor['advisorCgeCode']: advisor for advisor in self.advisor_data}
    
        # Iterar sobre as contas para encontrar a conta correspondente ao número fornecido
        for account in self.account_data:
            if account['account'] == account_number:
                # Encontrou a conta, agora associamos o assessor
                assessor_cge_code = account['sgCGE']
                
                # Se encontrar o assessor correspondente, retornamos as informações
                if assessor_cge_code in advisor_dict:
                    advisor = advisor_dict[assessor_cge_code]
                    return account['clientName'], advisor['advisorName'], advisor['email'], advisor['phone']
                else:
                    # Se não encontrar o assessor, retorna None para email e telefone
                    return account['clientName'], account['nome_assessor'], None, None
    
        # Caso o número da conta não seja encontrado, retorne valores padrão
        return None, None, None, None