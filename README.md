# PyGamentos

## Introdução

O PyGamentos é uma API de pagamentos de pequeno porte, desenvolvida com propósitos acadêmicos. Sua finalidade é simular transações entre usuários e fornecer recursos para o gerenciamento de pagamentos.

## Requisitos

Antes de prosseguir, certifique-se de ter as seguintes ferramentas instaladas em seu computador:

- [Docker](https://www.docker.com/get-started/)
- [Python 3+](https://www.python.org/)

Ambos os sites fornecem instruções detalhadas para a instalação.

## Configurando o Ambiente

Para configurar o ambiente e começar a trabalhar com o projeto, siga as etapas abaixo:

1. **Clonando o Projeto**

   Você pode clonar o repositório do projeto executando o seguinte comando no seu terminal:

   ```sh
   git clone "https://github.com/BarrosRichard/pygamentos.git"
   ```

2. **Criando um Ambiente Virtual**

   Antes de instalar as dependências, crie um ambiente virtual para isolar o ambiente de desenvolvimento. Dependendo do seu sistema operacional, você pode usar os seguintes comandos:

   No Windows (CMD):

   ```batch
   pip install virtualenv
   virtualenv pygamentos
   ```

   No Linux:

   ```sh
   sudo apt install python3-pip python3-virtualenv
   virtualenv pygamentos/
   ```

3. **Instalando Dependências**

   Após criar o ambiente virtual, ative-o e instale as dependências do projeto listadas no arquivo `requirements.txt`:

   ```sh
   source pygamentos/bin/activate  # No Linux
   .\pygamentos\Scripts\activate  # No Windows
   pip install -r requirements.txt
   ```

4. **Configurando Variáveis de Ambiente**

   Faça uma cópia do arquivo `.env.example` e renomeie-o para `.env`. Certifique-se de configurar as variáveis de ambiente necessárias no arquivo `.env` de acordo com suas necessidades.

5. **Iniciando o Banco de Dados**

   Você pode iniciar o container do MySQL configurado no arquivo `docker-compose.yml` com o seguinte comando:

   ```sh
   docker-compose up -d
   ```

6. **Aplicando Migrações do Banco de Dados** 

    Para criar as tabelas do banco de dados, você deve aplicar as migrações usando o Flask-Migrate. Certifique-se de que seu ambiente virtual esteja ativado e que você esteja no repositório `pygamentos/api`. Execute o seguinte comando:
    
	  ```sh
	  flask db upgrade
   ```

Agora, você está pronto para começar a trabalhar com o projeto PyGamentos. Certifique-se de seguir essas etapas na ordem e ajustar os comandos conforme necessário, dependendo do seu ambiente de desenvolvimento.