# Importando as classes e funções do código existente
from core.services.stock_orders_service import StockOrdersService, Order


# Configurando o teste para verificar a busca do nome do cliente
def test_client_name_retrieval():
    # Instanciando o serviço
    stock_orders_service = StockOrdersService()

    # Simulando uma ordem para uma conta específica
    test_order = Order(
        account="4153657",  # Insira uma conta existente para garantir a busca do nome
        symbol="ABCD",
        order_qty="100",
        order_price="10.5",
        side="Compra",
    )

    # Executando o método que agrupa ordens por cliente
    grouped_orders = stock_orders_service._group_orders_by_client([test_order])

    # Verificando o resultado
    for client_name, orders in grouped_orders.items():
        print(f"Nome do cliente encontrado: {client_name}")
        for order in orders:
            print(f"Detalhes da Ordem: {order}")


# Executando o teste
test_client_name_retrieval()

if __name__ == "__main__":
    test_client_name_retrieval()
