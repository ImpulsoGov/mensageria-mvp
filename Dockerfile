# Use a imagem base do Python
FROM python:3.10.8-slim-bullseye

# Instala o OpenVPN e dependências do sistema
RUN apt-get update && \
    apt-get install -y \
    curl \
    build-essential \
    libpq-dev 

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

ENV POETRY_VIRTUALENVS_CREATE 1
ENV POETRY_VIRTUALENVS_IN_PROJECT 0

# Instala o Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Define o PATH para incluir o diretório do Poetry
ENV PATH="/root/.local/bin:${PATH}"

# Copia os arquivos de configuração do Poetry
COPY pyproject.toml poetry.lock poetry.toml /app/

# Configura o número máximo de workers para a instalação do Poetry
RUN poetry config installer.max-workers 10

# Instala as dependências usando o Poetry
RUN poetry install --no-root

# Copia o código do aplicativo
COPY . /app

# Exponha a porta 5000
EXPOSE 5000

# Comando para iniciar o script de inicialização
CMD ["poetry", "run", "python", "app.py"]