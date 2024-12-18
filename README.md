# Backend - TIG - Integração API's BTG Pactual

Este projeto é uma solução de integração entre o escritório da **Top Investment Group** e a **API do BTG Pactual**. O sistema automatiza a chamada das API's, processa os dados e persiste num banco de dados. Conta com fluxo de autenticação configurado para a obtenção de tokens, 

Esta lista refere-se às API’s que estão integradas, e marcadas as que estão com sua funcionalidade validada.

**API de Relação de Produtos RF por Parceiro**

- [-] Relatórios de Títulos públicos
- [-] RF
- [-] Debêntures
- [-] CRA/CRI
- [-] Compromissadas

**API de Rentabilidade Diária**

- [ ] Rentabilidade Diária de parceiro
- [ ] Rentabilidade Diária de parceiro por data ref.

**API Base de Contas**

- [x] Todas as contas por parceiro, e se é do tipo Fundos

**API de Relatórios Gerenciais**

- [x] TIR Mensal por parceiro
    
- [x] Relatório de Posições
    
- [x] Base BTG
    
- [x] NNM Gerencial

- [x] Fundos
    

**API Produtos Estruturados**

- [ ] Relatórios de Custódia POR PARCEIRO.
    

**API STVM (New Net Money)**

- [ ] Info de STVM POR PARCEIRO e DATA
    

**API Relatórios Gerenciais de Comissões**

- [-] Relatório de Comissão dos últimos 4 dias
    

**API de Rentabilidade Mensal**

- [x] Rentabilidade das carteiras por período
    
- [ ] Rentabilidade dos produtos por período 
    

**API de Pré-Operações**

- [ ] Recupera todas as pré-operações de um parceiro
    

**API Movimentação**

- [ ] Todas as movimentações de UMA conta
    
- [ ] Todas as movimentações de UMA conta por período
    
- [ ] Movimentação de TODAS as contas por parceiro e data
    
- [ ] Movimentações de UMA conta por mercado e ativo
    

**API de Posição**

- [ ] Posições por conta
    
- [ ] Posições por conta e data
    
- [ ] Preço unitário por conta e período de Renda Fixa
    
- [ ] Busca histórica de preço unitário por conta e período de Renda Fixa
    
- [ ] Posições por parceiro
    
- [ ] Histórico completo de posições por parceiro
    

**API Debêntures**

- [ ] Debêntures por data de referência
    

**API Ordens da Bolsa** 

**API Operações**

- [ ] Lista últimas operações por parceiro 
    

**API Suitability**

- [x] Perfil de risco atual do investidor
    
- [x] Perfil e validade de risco atual do investidor
    

**API Dados Cadastrais**

- [x] Busca informações de uma conta, como Nome, E-mail, Telefone, etc..
    

**API de Seguro de Vida**

- [ ] Posição de Seguro de Vida por conta
    

**API Relacionamento de Conta e Parceiro**

- [x] Contas e seus assessores
    
- [x] Contas por CGE
    

**API PUSH e Reservas de IPO**

- [ ] Push de ofertas ativas de IPO
    
- [ ] Reservas de ofertas ativas de IPO
    

**API de Análise de Carteira Recomendada**

- [ ] Retorna recomendações de produtos