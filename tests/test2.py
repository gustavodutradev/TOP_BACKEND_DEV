import unittest
import json
from utils.search_advisor_email import (
    SearchAdvisorEmail,
)  # Ajuste o caminho se necessário


class TestSearchAdvisorEmail(unittest.TestCase):

    def setUp(self):
        # Instancia a classe que contém o método a ser testado
        self.service = SearchAdvisorEmail()

        # Carregar os dados dos arquivos JSON
        with open("resources/data/advisors_data.json", "r") as f:
            self.advisor_data = json.load(f)

        with open("resources/data/account_advisors_data.json", "r") as f:
            self.account_advisor_data = json.load(f)

    def test_get_client_and_advisor_info_success(self):
        # Defina o número da conta para testar
        account_number = (
            "4050689"  # Número de conta no arquivo account_advisors_data.json
        )

        # Chama o método que queremos testar
        client_name, advisor_name, advisor_email, sgcge = (
            self.service.get_client_and_advisor_info(account_number)
        )

        # Verifique os resultados para garantir que estão corretos
        self.assertEqual(client_name, "TIAGO FRANCISCO DIAS REZENDE")
        self.assertEqual(advisor_name, "LUCAS VINICIUS ROCHA MARQUES")
        self.assertEqual(advisor_email, "lucasmarques@topinvgroup.com")
        self.assertEqual(sgcge, "799948")

    # def test_get_client_and_advisor_info_no_sgcge(self):
    #     # Defina um número de conta que não existe no arquivo
    #     account_number = "9999999"

    #     # Chama o método
    #     client_name, advisor_name, advisor_email, sgcge = self.service.get_client_and_advisor_info(account_number)

    #     # Verifique o retorno para o caso em que o CGE não é encontrado
    #     self.assertEqual(client_name, None)
    #     self.assertIsNone(advisor_name)
    #     self.assertIsNone(advisor_email)
    #     self.assertIsNone(sgcge)

    # def test_get_client_and_advisor_info_no_advisor(self):
    #     # Defina um número de conta que leva a um CGE válido, mas sem um assessor correspondente
    #     account_number = "4153657"

    #     # Modifique os dados do arquivo advisor_data para que não haja um assessor correspondente ao CGE
    #     original_advisor_data = self.advisor_data[:]
    #     self.advisor_data = []  # Remova o assessor para simular o erro

    #     # Chama o método
    #     client_name, advisor_name, advisor_email, sgcge = self.service.get_client_and_advisor_info(account_number)

    #     # Restaura os dados originais
    #     self.advisor_data = original_advisor_data

    #     # Verifique o retorno para o caso em que o assessor não é encontrado
    #     self.assertEqual(client_name, "MARIA SILVIA MAZONI GUIMARAES")
    #     self.assertIsNone(advisor_name)
    #     self.assertIsNone(advisor_email)
    #     self.assertEqual(sgcge, "587877")

    # def test_get_client_and_advisor_info_partial_advisor_info(self):
    #     # Defina um número de conta que leva a um assessor com nome, mas sem email
    #     account_number = "4153657"

    #     # Modifique os dados do arquivo advisor_data para que o assessor não tenha e-mail
    #     original_advisor_data = self.advisor_data[:]
    #     self.advisor_data[0]["email"] = None  # Remova o e-mail do assessor

    #     # Chama o método
    #     client_name, advisor_name, advisor_email, sgcge = self.service.get_client_and_advisor_info(account_number)

    #     # Restaura os dados originais
    #     self.advisor_data = original_advisor_data

    #     # Verifique o retorno para o caso onde o assessor tem nome, mas não tem e-mail
    #     self.assertEqual(client_name, "MARIA SILVIA MAZONI GUIMARAES")
    #     self.assertEqual(advisor_name, "JOAO EVANGELISTA ASSUMPCAO TEIXEIRA NETO")
    #     self.assertIsNone(advisor_email)
    #     self.assertEqual(sgcge, "587877")


if __name__ == "__main__":
    unittest.main()
