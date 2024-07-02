# Otimizador de Time do Cartola FC

Este projeto visa otimizar a seleção de um time no Cartola FC com base no orçamento disponível e nas médias de desempenho dos jogadores. O script realiza a otimização usando a biblioteca `pulp` para programação linear inteira (LPI) e envia os resultados por email.

## Funcionalidades

- **Busca de Dados**: O script obtém os dados dos jogadores disponíveis no mercado do Cartola FC através de uma API.
- **Otimização do Time**: Utiliza Programação Linear Inteira (LPI) para selecionar os melhores jogadores dentro de um orçamento específico. A LPI é uma técnica de otimização onde a função objetivo e as restrições são lineares, e as variáveis de decisão são inteiras. Neste caso, a função objetivo é maximizar a média dos jogadores escolhidos, respeitando as restrições de orçamento e a quantidade de jogadores por posição.
- **Envio de Email**: Gera um email formatado em HTML com a lista dos jogadores selecionados e suas estatísticas e envia para um destinatário especificado.

## Dependências

- `requests`
- `json`
- `pulp`
- `python-dotenv`

## Instalação

1. Clone o repositório:
    ```sh
    git clone https://github.com/usuario/repositorio.git
    cd repositorio
    ```

2. Crie um ambiente virtual e instale as dependências:
    ```sh
    python -m venv venv
    source venv/bin/activate  # No Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3. Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
    ```env
    EMAIL_FROM=seu_email@example.com
    EMAIL_TO=email_destinatario@example.com
    EMAIL_KEY=sua_chave_de_email ( Senha de app no gmail )
    ```

## Uso

1. Execute o script principal:
    ```sh
    python main.py
    ```

2. O script buscará os dados dos jogadores disponíveis, otimizará a seleção do time com base no orçamento e nas posições necessárias, e enviará um email com os resultados.

## Estrutura do Projeto

```plaintext
.
├── main.py                 # Script principal
├── email_sender.py         # Classe Emailer para enviar emails
├── .env                    # Variáveis de ambiente (não incluir no controle de versão)
├── requirements.txt        # Lista de dependências
└── README.md               # Este arquivo README
