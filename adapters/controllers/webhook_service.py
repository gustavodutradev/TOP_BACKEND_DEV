from core.services.token_service import TokenService
from utils.logging import Logger


class WebhookService:

    def __init__(self, app) -> None:
        self.app = app
        self.token_service = TokenService()
        self.register_routes()
        self.Logger = Logger(app)
        # self.setup_logging()

    # def setup_logging(self):
    #     logging.basicConfig(level=logging.DEBUG)
    #     self.logger = logging.getLogger(__name__)

    # def log_and_respond(self, event_name: str):
    #     try:
    #         # Captura o JSON da requisição e verifica se está no formato esperado
    #         data = request.get_json(force=True, silent=True)

    #         # Se o JSON não estiver presente ou for inválido, retorna um erro 400
    #         if not data:
    #             self.app.logger.error(
    #                 f"Received Event {event_name} - No JSON payload found"
    #             )
    #             return (
    #                 jsonify(
    #                     {
    #                         "status": "Invalid request",
    #                         "message": "No JSON payload found",
    #                     }
    #                 ),
    #                 400,
    #             )

    #         # Verifica se 'data' é uma lista e pega o primeiro item, se aplicável
    #         if isinstance(data, list) and len(data) > 0:
    #             data = data[0]

    #         # Tenta obter a URL diretamente ou via campo 'response'
    #         url = data.get("url") or data.get("response", {}).get("url")

    #         if not url:
    #             # Acessa com segurança a lista 'errors' e verifica se há pelo menos um erro
    #             errors = data.get("errors", [{}])
    #             error = errors[0] if isinstance(errors, list) and errors else {}

    #             # Coleta a mensagem e código de erro, com valores padrão
    #             message = error.get("message", "Unknown error")
    #             code = error.get("code", "Unknown code")

    #             # Log detalhado do evento e erro
    #             self.app.logger.warning(
    #                 f"Received Event {event_name} - URL not found in request data. "
    #                 f"Error Code: {code}, Message: {message}, Full Payload: {data}"
    #             )

    #             # Responde com o código de erro apropriado
    #             return jsonify({"status": code, "message": message}), 400

    #         # Loga o sucesso com a URL recebida
    #         self.logger.info(
    #             f"Received Event {event_name} - URL: {url}, Full Payload: {data}"
    #         )

    #         # Retorna sucesso quando o evento é processado corretamente
    #         return (
    #             jsonify(
    #                 {"status": "success", "message": "Event processed", "url": url}
    #             ),
    #             200,
    #         )

    #     except Exception as e:
    #         # Loga a exceção ocorrida durante o processamento da requisição
    #         self.app.logger.error(f"Exception on {event_name} - {str(e)}")
    #         return jsonify({"status": "error", "message": "Internal server error"}), 500

    def register_routes(self):

        ## Relatórios Gerenciais
        @self.app.route("/api/v1/rg-tir-mensal-parceiro", methods=["POST"])
        def monthly_tir():
            return Logger.log_and_respond("RG - TIR_MENSAL")

        @self.app.route("/api/v1/rg-posicoes", methods=["POST"])
        def positions():
            return Logger.log_and_respond("RG - POSICOES")

        @self.app.route("/api/v1/rg-base-btg", methods=["POST"])
        def base_btg():
            return Logger.log_and_respond("RG - BASE BTG")

        @self.app.route("/api/v1/rg-nnm-gerencial", methods=["POST"])
        def nnm_gerencial():
            return Logger.log_and_respond("RG - NNM GERENCIAL")

        @self.app.route("/api/v1/rg-fundos", methods=["POST"])
        def fundos():
            return Logger.log_and_respond("RG - FUNDOS")

        @self.app.route("/api/v1/rg-cra-cri", methods=["POST"])
        def cra_cri():
            return Logger.log_and_respond("RG - CRA/CRI")

        ## Rentabilidade Diária
        @self.app.route("/api/v1/daily-profit", methods=["POST"])
        def daily_profit():
            return Logger.log_and_respond("Daily Profit")

        @self.app.route("/api/v1/daily-profit-by-date", methods=["POST"])
        def daily_profit_by_date():
            return Logger.log_and_respond("Daily Profit by Date")

        ## Relatórios de Custódia
        @self.app.route("/api/v1/custody", methods=["POST"])
        def custody():
            return Logger.log_and_respond("Custody")

        @self.app.route("/api/v1/custody-by-date", methods=["POST"])
        def custody_by_date():
            return Logger.log_and_respond("Custody by Date")

        ## Relatório STVM New NET Money
        @self.app.route("/api/v1/stvm", methods=["POST"])
        def stvm():
            return Logger.log_and_respond("STVM")

        ## Comissoes dos ultimos 4 dias
        @self.app.route("/api/v1/comissions", methods=["POST"])
        def commissions():
            return Logger.log_and_respond("Commissions")

        ## Rentabilidade Mensal
        @self.app.route("/api/v1/monthly-customer-profit", methods=["POST"])
        def monthly_customer_profit():
            return Logger.log_and_respond("Monthly Customer Profit")

        @self.app.route("/api/v1/monthly-product-profit", methods=["POST"])
        def monthly_product_profit():
            return Logger.log_and_respond("Monthly Product Profit")

        ## Pré Operações
        @self.app.route("/api/v1/pre-operations", methods=["POST"])
        def pre_operations():
            return Logger.log_and_respond("Pre-Operations")

        ## Reservas de IPO
        @self.app.route("/api/v1/push-ofertas-ativas", methods=["POST"])
        def push_ofertas_ativas():
            return Logger.log_and_respond("Ofertas Ativas de IPO")

        @self.app.route("/api/v1/reservas-ofertas-ativas", methods=["POST"])
        def reservas_ofertas_ativas():
            return Logger.log_and_respond("Reservas de Ofertas Ativas")

        ## Ordens da Bolsa
        # @self.app.route("/api/v1/orders", methods=["POST"])
        # def orders():
        #     return Logger.log_and_respond("Orders")

        ## Operações
        @self.app.route("/api/v1/operations", methods=["POST"])
        def operations_all_accounts():
            return Logger.log_and_respond("Operations (All Accounts)")

        ## Relacionamento de Conta e Parceiro
        @self.app.route("/api/v1/relationship-accounts-advisors", methods=["POST"])
        def relationship_accounts_advisors():
            return Logger.log_and_respond("Relationship Accounts and Advisors")
