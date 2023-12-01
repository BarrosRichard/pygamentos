from datetime import datetime
import fire
from rich.console import Console
from rich.table import Table
from rich import box
import requests
import getpass
import json
import pickle
import os
import zipfile

_BASE_URL = 'http://localhost:5000'
console = Console()

def _set_password():
    while True:
        password = getpass.getpass("Digite sua senha (mínimo 6 caracteres): ")
        if len(password) >= 6:
            return password
        else:
            print("A senha deve ter pelo menos 6 caracteres. Tente novamente.")

def _confirm_password(password):
    confirmation = getpass.getpass("Confirme sua senha: ")
    if confirmation == password:
        print("Senha confirmada com sucesso!")
        return True
    else:
        print("As senhas não coincidem. Tente novamente.")
        return False
    
def _save_state(state):
     with open("cache/http.pkl", "wb") as f:
        pickle.dump(state, f)

def _ord_by_date(item):
    return datetime.strptime(item['datetime'], '%Y-%m-%d %H:%M:%S')

def _get_default_download_path():
    user_name = os.getlogin()

    download_path = os.path.join("C:\\Users", user_name, "Downloads")

    return download_path

class PyGamentos:
    def __init__(self) -> None:
        self._http = requests.Session()
        self._set_header()

        if os.path.exists('cache/http.pkl'):
            with open("cache/http.pkl", "rb") as f:
                self._http = pickle.load(f)

    def _set_header(self) -> None:
        self._http.headers = {
            'Content-Type': 'application/json',
            'Authorization': ''
        }

    def deposit(self) -> None:
        """Realiza um depósito de fundos na conta do usuário.

        Sintaxe:
            pygamentos deposit

        Descrição:
            Este comando permite ao usuário realizar um depósito de fundos em sua conta. 
            Se o usuário estiver autenticado, será solicitado a inserir o valor desejado. 
            Em seguida, o valor é enviado para o servidor, que processa a transação. 
            
            Observação: O usuário deve estar autenticado para utilizar este comando.

        Exemplo:
            pygamentos deposit
        """
        try:
            if self._http.headers['Authorization'] != "":
                amount = float(input("Valor para depósito: "))

                print(f'\nDetalhes do Depósito:')
                print(f'Valor: R$ {amount}')
                
                if str(input('Confirma o depósito? (S/n)... ')).lower() == 's':
                    response = self._http.post(f'{_BASE_URL}/transaction/deposit', json={'amount': amount})
                    response = json.loads(response.text)

                    if response['code'] == 200:
                        print('Depósito realizado com sucesso.')
                    else:
                        print(f'Erro ao efetuar depósito: {response["message"]}')
                else:
                    print('Depósito cancelado.')
            else:
                print("Faça login primeiro.")
        except ValueError:
            print('Valor inválido. Certifique-se de inserir um valor numérico.')
        except Exception as e:
            print(f'Erro inesperado: {str(e)}')

    def balance(self) -> None:
        """Recupera e exibe o saldo da conta do usuário juntamente com transações recentes.

        Sintaxe:
            pygamentos balance

        Descrição:
            Este comando recupera e exibe o saldo atual da conta do usuário, assim como suas transações mais recentes.
            Se o usuário estiver autenticado, a tabela de transações, contendo informações como ID, Tipo, Descrição, Valor e Horário.
            será exibida ordenada por data de forma decrescente. O saldo atual também será apresentado no início da saída.

        Observação: O usuário deve estar autenticado para utilizar este comando.

        Exemplo:
            pygamentos balance
        """
        try:
            if self._http.headers['Authorization'] != "":
                response = self._http.get(f'{_BASE_URL}/transaction/get_balance')
                response = json.loads(response.text)

                if 'data' not in response:
                    console.print(f"[red]Erro: {response['message']}[/red]")
                    return

                table = Table(title="Transações Recentes", box=box.SIMPLE_HEAVY, show_lines=True, header_style="bold magenta")
                table.add_column("ID", justify="left", style="cyan", no_wrap=True)
                table.add_column("Tipo", justify="left", style="cyan", no_wrap=True)
                table.add_column("Descrição", justify="left", style="cyan")
                table.add_column("Valor", justify="right", style="cyan", no_wrap=True)
                table.add_column("Pago para / Recebido de", justify="left", style="cyan", no_wrap=True)
                table.add_column("Horário", justify="left", style="cyan")

                balance = response['data']['balance']
                transactions = sorted(response['data']['payments'] + response['data']['received'], key=_ord_by_date, reverse=True)

                for data in transactions:
                    amount_text = f"R$ {data['amount']}"
                    if data['type'] == 'RECEBIDA':
                        amount_text = f"[green]{amount_text}[/green]"
                    elif data['type'] == 'PAGAMENTO':
                        amount_text = f"[red]{amount_text}[/red]"

                    table.add_row(str(data['id']), data['type'], data['description'], amount_text, data['paid_for_received_from'] , data['datetime'])

                balance_text = f"Saldo: R${balance}"
                if balance < 0:
                    balance_text = f"[red]{balance_text}[/red]"
                elif balance > 0:
                    balance_text = f"[green]{balance_text}[/green]"

                console.print("\n" + balance_text)
                console.print(table)

            else:
                console.print("Faça login primeiro.")
        except Exception as e:
            console.print(f"[red]Erro: Ocorreu uma exceção - {e}[/red]")

    def pixkeys(self) -> None:
        """Recupera e exibe as Chaves Pix associadas à conta do usuário.

        Sintaxe:
            pygamentos pixkeys

        Descrição:
            Este comando recupera e exibe as Chaves Pix associadas à conta do usuário.
            Se o usuário estiver autenticado, uma tabela será apresentada com as colunas de ID, Tipo e Chave.
            Cada linha representa uma Chave Pix registrada na conta.

        Observação: O usuário deve estar autenticado para utilizar este comando.

        Exemplo:
            pygamentos pixkeys
        """
        try:
            if self._http.headers['Authorization'] != "":
                response = self._http.get(f'{_BASE_URL}/pixkey/get_pixkeys')
                response = json.loads(response.text)

                if 'data' not in response:
                    console.print(f"[red]Erro: {response['message']}[/red]")
                    return

                if response['data']:
                    table = Table(title='Chaves Pix', box=box.SIMPLE_HEAVY, show_lines=True, header_style="bold magenta")

                    table.add_column("ID", justify="left", style="cyan", no_wrap=True)
                    table.add_column("Tipo", justify="left", style="cyan", no_wrap=True)
                    table.add_column("Chave", justify="right", style="cyan")

                    for data in response['data']:
                        table.add_row(str(data['id']), data['type'], data['key'])

                    console.print(table)
                else:
                    console.print("[yellow]Nenhuma chave pix registrada. Execute 'add_pixkey'.[/yellow]")
            else:
                console.print("Faça login primeiro.")
        except Exception as e:
            console.print(f"[red]Erro: Ocorreu uma exceção - {e}[/red]")

    def add_pixkey(self) -> None:
        """Adiciona uma nova Chave Pix à conta do usuário.

        Sintaxe:
            pygamentos add_pixkey

        Descrição:
            Este comando permite ao usuário adicionar uma nova Chave Pix à sua conta.
            Se o usuário estiver autenticado, será apresentada uma lista de tipos de chave disponíveis,
            e o usuário deverá selecionar um digitando o número correspondente. Em seguida, será solicitado
            que o usuário insira a chave.

        Observação: O usuário deve estar autenticado para utilizar este comando.

        Exemplo:
            pygamentos add_pixkey
        """
        try:

            if self._http.headers['Authorization'] != "":
                pixkey_types = self._http.get(f'{_BASE_URL}/pixkey/get_pixkey_types')
                pixkey_types = json.loads(pixkey_types.text)['data']

                console.print('Selecione um tipo de chave:\n')

                for data in pixkey_types:
                    console.print(f'{data["id"]}. {data["description"]}')

                pixkey_type = int(input("... "))

                if any(d['id'] == pixkey_type for d in pixkey_types):
                    pixkey_value = str(input("Digite sua chave: "))
                    if str(input(f'Registrar chave pix? (S/n)... ')).lower() == 's':
                        response = self._http.post(f'{_BASE_URL}/pixkey/add_pixkey', json={'key_type_id': pixkey_type, 'key': pixkey_value})
                        response = json.loads(response.text)

                        if 'status' not in response:
                            console.print(f"[red]Erro: {response['message']}[/red]")
                            return

                        console.print(f"{response['status']}: {response['message']}")
                    else:
                        print('\n[CANCELED]')
            else:
                console.print("Faça login primeiro.")
        except Exception as e:
            console.print(f"[red]Erro: Ocorreu uma exceção - {e}[/red]")

    def transaction(self) -> None:
        """Inicia o processo de uma transferência entre usuários.

        Sintaxe:
            pygamentos transaction

        Descrição:
            Este comando permite ao usuário iniciar uma transferência entre contas. O usuário será guiado para escolher
            o tipo de transferência, a chave Pix do destinatário e o valor a ser transferido.
            Antes de finalizar a transação, será exibida uma mensagem de confirmação com os detalhes da transferência.

        Exemplo:
            pygamentos transaction
        """
        try:

            if self._http.headers['Authorization'] != "":
                transaction_types = self._http.get(f'{_BASE_URL}/transaction/get_transaction_types')
                transaction_types = json.loads(transaction_types.text)['data']

                console.print('Selecione um tipo de transferência:\n')

                for data in transaction_types:
                    console.print(f'{data["id"]}. {data["description"]}')

                transaction_type = int(input("... "))

                if any(d['id'] == transaction_type for d in transaction_types):
                    pixkey = str(input("Chave pix: "))
                    check_pixkey = self._http.get(f'{_BASE_URL}/pixkey/search_pixkey', json={'pixkey': pixkey})
                    check_pixkey = json.loads(check_pixkey.text)
                    if check_pixkey['code'] == 200:
                        amount = float(input("Valor da transferência: "))
                        
                        if transaction_type == 2:
                            credit_cards = self._http.get(f'{_BASE_URL}/credit_card/get_credit_cards')
                            credit_cards = json.loads(credit_cards.text)['data']

                            if not credit_cards:
                                console.print("Nenhum cartão de crédito registrado. Adicione um cartão de crédito:")
                                return

                            console.print('Selecione um cartão de crédito:\n')

                            for card in credit_cards:
                                console.print(f'{card["id"]}. **** **** **** {card["number"][-4:]} {card["description"]}')

                            card_id = int(input("... "))
                            selected_card = next((card for card in credit_cards if card["id"] == card_id), None)

                            if not selected_card:
                                console.print("Cartão de crédito não encontrado.")
                                return
                            
                            transaction_tax = self._http.get(f'{_BASE_URL}/transaction/get_transaction_tax', json={'transaction_type_id': transaction_type})
                            transaction_tax = json.loads(transaction_tax.text)

                            total_amount_with_tax = amount * (1 + transaction_tax['data']['tax'])
                            total_amount_with_tax_str = f'R$ {total_amount_with_tax:.2f}'

                            console.print(f'\nDetalhes da transferência:')
                            console.print(f'Taxa por crédito: {transaction_tax["data"]["tax"] * 100}%')
                            console.print(f'Destinatário: {check_pixkey["data"]["username"]}')
                            console.print(f'Valor da transferência: {total_amount_with_tax_str}\n')


                            confirmation = input(f'Tem certeza que deseja transferir para @{check_pixkey["data"]["username"]} usando o cartão de crédito terminado em **** {selected_card["number"][-4:]} {selected_card["description"]}? (S/n)... ')
                            if confirmation.lower() == 's':
                                response = self._http.post(f'{_BASE_URL}/transaction/send_transaction', json={'receiver': check_pixkey['data']['id'], 'amount': amount, 'transaction_type': transaction_type, 'credit_card_id': selected_card['id']})
                                response = json.loads(response.text)

                                if 'status' not in response:
                                    console.print(f"[red]Erro: {response['message']}[/red]")
                                    return

                                console.print(f"{response['status']}: {response['message']}")
                            else:
                                console.print('\n[CANCELED]')
                        else:
                            console.print(f'\nDetalhes da transferência:')
                            console.print(f'Destinatário: {check_pixkey["data"]["username"]}')
                            console.print(f'Valor da transferência: {amount}\n')

                            confirmation = input(f'Tem certeza que deseja transferir para @{check_pixkey["data"]["username"]}? (S/n)... ')
                            if confirmation.lower() == 's':
                                response = self._http.post(f'{_BASE_URL}/transaction/send_transaction', json={'receiver': check_pixkey['data']['id'], 'amount': amount, 'transaction_type': transaction_type})
                                response = json.loads(response.text)

                                if 'status' not in response:
                                    console.print(f"[red]Erro: {response['message']}[/red]")
                                    return

                                console.print(f"{response['status']}: {response['message']}")
                            else:
                                console.print('\n[CANCELED]')
                    else:
                        console.print(f"[red]Erro: {check_pixkey['message']}[/red]")
            else:
                console.print("Faça login primeiro.")
        except Exception as e:
            console.print(f"[red]Erro: Ocorreu uma exceção - {e}[/red]")

    def add_credit_card(self) -> None:
        """Adiciona um cartão de crédito à conta do usuário.

        Sintaxe:
            pygamentos add_credit_card

        Descrição:
            Este comando permite ao usuário adicionar um cartão de crédito à sua conta.
            Serão solicitadas as informações necessárias, como número do cartão, data de validade e CVV.
            Após adicionar o cartão com sucesso, ele estará disponível para ser selecionado durante as transações.

        Exemplo:
            pygamentos add_credit_card
        """
        try:
            console = Console()

            if self._http.headers['Authorization'] != "":
                console.print("Informe os detalhes do cartão de crédito:\n")

                number = input("Número do cartão: ")
                validate = input("Data de validade (MM/YY): ")
                cvv = input("CVV: ")
                description = input("Descrição (opcional): ")

                response = self._http.post(f'{_BASE_URL}/credit_card/add_credit_card', json={'number': number, 'validate': validate, 'cvv': cvv, 'description': description})
                response = json.loads(response.text)

                if 'status' not in response:
                    console.print(f"[red]Erro: {response['message']}[/red]")
                    return

                console.print(f"{response['status']}: {response['message']}")
            else:
                console.print("Faça login primeiro.")
        except Exception as e:
            console.print(f"[red]Erro: Ocorreu uma exceção - {e}[/red]")

    def credit_cards(self) -> None:
        """Lista os cartões de crédito associados à conta do usuário.

        Sintaxe:
            pygamentos credit_cards

        Descrição:
            Este comando permite ao usuário visualizar a lista de cartões de crédito associados à sua conta.
            Cada cartão é exibido com um identificador único, número parcial do cartão e descrição (se disponível).

        Exemplo:
            pygamentos credit_cards
        """
        try:

            if self._http.headers['Authorization'] != "":
                response = self._http.get(f'{_BASE_URL}/credit_card/get_credit_cards')
                response = json.loads(response.text)

                if 'code' not in response:
                    console.print(f"[red]Erro: {response['message']}[/red]")
                    return

                if response['code'] == 200:
                    credit_cards = response['data']

                    table = Table(title="Lista de Cartões de Crédito", show_lines=True)
                    table.add_column("ID", justify="left")
                    table.add_column("Número", justify="left")
                    table.add_column("Descrição", justify="left")

                    for card in credit_cards:
                        table.add_row(str(card['id']), f"**** **** **** {card['number'][-4:]}", card['description'])

                    console.print(table)

                else:
                    console.print(response['message'])

            else:
                console.print("Faça login primeiro.")

        except Exception as e:
            console.print(f"[red]Erro ao listar cartões de crédito: {e}[/red]")

    def export_transactions(self) -> None:
        
        """Exporta dados das transações do usuário.

            Sintaxe:
                pygamentos export_transactions

            Descrição:
                Este comando permite ao usuário exportar dados completos das suas transações para um arquivo JSON.
                Após a exportação, o arquivo é salvo no diretório padrão de downloads do sistema, e o nome do arquivo
                contém a data e hora da exportação para garantir a unicidade dos arquivos.

            Exemplo:
                pygamentos export_transactions
        """
        try:

            if self._http.headers['Authorization'] != "":
                console.print("Exportando dados...")
                response = self._http.get(f'{_BASE_URL}/transaction/get_full_transaction')
                response = json.loads(response.text)

                if response['code'] == 200:
                    zip_file_path = os.path.join(_get_default_download_path(), f'transaction_{datetime.now().strftime("%Y-%M-%d_%H-%M-%S")}.zip')
                    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        zipf.writestr('transaction_data.json', json.dumps(response['data']))
                        
                    console.print(f"Exportado com sucesso para {_get_default_download_path()}")
                else:
                    console.print(f"[red]Erro ao exportar lista de transações.")
            else:
                console.print("Faça login primeiro.")

        except Exception as e:
            console.print(f"[red]Erro ao exportar lista de transações: {e}[/red]")

    def register(self, username) -> None:
        """Registra uma nova conta de usuário. PARAMS: [username]

        Sintaxe:
            pygamentos register [username]

        Descrição:
            Este comando permite ao usuário registrar uma nova conta fornecendo um nome de usuário.
            Se o usuário já estiver autenticado, será exibida a mensagem "Saia para registrar uma nova conta."
            e nenhum registro será realizado. Caso contrário, o usuário será solicitado a inserir e confirmar
            uma senha com pelo menos 6 caracteres. Após a confirmação da senha, a conta será registrada e uma
            mensagem de confirmação será exibida.

        Observação: O usuário não deve estar autenticado para utilizar este comando.

        Exemplo:
            pygamentos register novo_usuario
        """
        try:
            console = Console()

            if self._http.headers['Authorization'] == "":
                password = _set_password()
                confirmated = _confirm_password(password)

                while not confirmated:
                    password = _set_password()
                    confirmated = _confirm_password(password)

                data = {
                    'username': username,
                    'password': password
                }

                response = self._http.post(f'{_BASE_URL}/auth/register', json=data)
                response = json.loads(response.text)

                if 'status' in response and 'message' in response:
                    console.print(f'{response["status"]}: {response["message"]}')
                else:
                    console.print(f'[red]Erro desconhecido ao registrar a conta.[/red]')

            else:
                console.print('Saia para registrar uma nova conta.')

            _save_state(self._http)

        except Exception as e:
            console.print(f'[red]Erro ao registrar a conta: {e}[/red]')

    def login(self, username) -> None:
        """Realiza o login em uma conta de usuário. PARAMS: [username]

        Sintaxe:
            pygamentos login [username]

        Descrição:
            Este comando permite ao usuário fazer login em uma conta existente fornecendo o nome de usuário.
            Se o usuário já estiver autenticado, será exibida a mensagem "Saia para entrar em outra conta."
            e nenhum login será realizado. Caso contrário, o usuário será solicitado a inserir sua senha.
            Após a verificação bem-sucedida, o usuário estará autenticado e uma mensagem de confirmação será exibida.

        Observação: O usuário não deve estar autenticado para utilizar este comando.

        Exemplo:
            pygamentos login usuario_existente
        """
        try:
            console = Console()

            if self._http.headers['Authorization'] == "":
                password = getpass.getpass("Digite sua senha: ")

                data = {
                    'username': username,
                    'password': password
                }

                response = self._http.post(f'{_BASE_URL}/auth/login', json=data)
                response = json.loads(response.text)

                if 'code' in response and 'status' in response and 'message' in response:
                    if response['code'] == 200:
                        self._http.headers['Authorization'] = response['data']['token']
                        console.print(f'{response["status"]}: {response["message"]}')
                    else:
                        console.print(f'{response["status"]}: {response["message"]}')
                else:
                    console.print(f'[red]Erro desconhecido ao realizar o login.[/red]')
            else:
                console.print("Saia para entrar em outra conta.")

            _save_state(self._http)

        except Exception as e:
            console.print(f'[red]Erro ao realizar o login: {e}[/red]')

    def logout(self) -> None:
        """Realiza o logout de uma conta de usuário.

        Sintaxe:
            python script.py logout

        Descrição:
            Este comando permite ao usuário fazer logout de uma conta autenticada.
            Se o usuário estiver autenticado, será exibida uma mensagem de confirmação antes de realizar o logout.

        Exemplo:
            python script.py logout
        """
        try:
            console = Console()

            if self._http.headers['Authorization'] != '':
                if str(input('Deseja mesmo sair? (S/n)... ')).lower() == 's': 
                    self._http.headers['Authorization'] = ''
                    console.print('success: Deslogado com sucesso.')
                else:
                    console.print('Operação de logout cancelada.')
            else:
                console.print('error: Nenhum usuário logado.')

            _save_state(self._http)

        except Exception as e:
            console.print(f'[red]Erro ao realizar o logout: {e}[/red]')

    def about(self) -> None:
        """
        Sobre o Pygamentos

        Desenvolvedores:
            - Richard Barros
            - Paulo Christian
            - Marcos Vinicius

        Tema:
        Pygamentos é uma aplicação de pagamento digital projetada para oferecer uma experiência eficiente e segura no gerenciamento de transações financeiras. Seu objetivo principal é simplificar a forma como os usuários lidam com pagamentos, transferências e outras operações financeiras, proporcionando uma plataforma intuitiva e de fácil utilização.

        Objetivo:
        O Pygamentos busca proporcionar aos usuários uma solução abrangente e prática para gerenciar suas finanças de maneira eficiente. A aplicação visa simplificar transações cotidianas, como transferências entre usuários, consulta de saldo e visualização de histórico de transações. Ao focar na usabilidade e na segurança, o Pygamentos aspira ser a escolha ideal para indivíduos que buscam uma maneira rápida e confiável de lidar com suas operações financeiras diárias.
        """
        about_text = """Sobre o Pygamentos
Desenvolvedores:
    - Richard Barros
    - Paulo Christian
    - Marcos Vinicius

Tema:
Pygamentos é uma aplicação de pagamento digital projetada para oferecer uma experiência eficiente e segura no gerenciamento de transações financeiras.
Seu objetivo principal é simplificar a forma como os usuários lidam com pagamentos, transferências e outras operações financeiras,
proporcionando uma plataforma intuitiva e de fácil utilização.

Objetivo:
O Pygamentos busca proporcionar aos usuários uma solução abrangente e prática para gerenciar suas finanças de maneira eficiente.
A aplicação visa simplificar transações cotidianas, como transferências entre usuários, consulta de saldo e visualização de histórico de transações.
Ao focar na usabilidade e na segurança, o Pygamentos aspira ser a escolha ideal para indivíduos que buscam uma maneira rápida e confiável de lidar com suas operações financeiras diárias.
"""
        console.print(about_text, style="bold green")

if __name__ == '__main__':
    try:
        fire.Fire(PyGamentos)
    except KeyboardInterrupt:
        console.print('\n[CANCELED]')