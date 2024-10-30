# Use a imagem base do Python
FROM python:3.10.8-slim-bullseye

# Instala o OpenVPN e dependências do sistema
RUN apt-get update && \
    apt-get install -y \
    curl \
    gcc \
    g++ \
    build-essential \
    libpq-dev 

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

ENV POETRY_VIRTUALENVS_CREATE 1
ENV POETRY_VIRTUALENVS_IN_PROJECT 0

# Definindo argumentos de build
ARG PROJECT_ID
ARG TEMPLATE_NAMESPACE
ARG ENV_PAULORAMOS_MA
ARG ENV_LAGOVERDE_MA
ARG ENV_PACOTI_CE
ARG ENV_MONSENHORTABOSA_CE
ARG ENV_MARAJADOSENA_MA
ARG ENV_ALAGOINHA_PE
ARG ENV_BARAUNA_RN
ARG ENV_JUCURUCU_BA
ARG ENV_VITORINOFREIRE_MA
ARG ENV_BREJODEAREIA_MA
ARG ENV_OIAPOQUE_AP
ARG ENV_TARRAFAS_CE
ARG ENV_SALVATERRA_PA
ARG ENV_LAGOADOOURO_PE

# Passando os argumentos para variáveis de ambiente
ENV PROJECT_ID=$PROJECT_ID
ENV TEMPLATE_NAMESPACE=$TEMPLATE_NAMESPACE
ENV ENV_PAULORAMOS_MA=$ENV_PAULORAMOS_MA
ENV ENV_LAGOVERDE_MA=$ENV_LAGOVERDE_MA
ENV ENV_PACOTI_CE=$ENV_PACOTI_CE
ENV ENV_MONSENHORTABOSA_CE=$ENV_MONSENHORTABOSA_CE
ENV ENV_MARAJADOSENA_MA=$ENV_MARAJADOSENA_MA
ENV ENV_ALAGOINHA_PE=$ENV_ALAGOINHA_PE
ENV ENV_BARAUNA_RN=$ENV_BARAUNA_RN
ENV ENV_JUCURUCU_BA=$ENV_JUCURUCU_BA
ENV ENV_VITORINOFREIRE_MA=$ENV_VITORINOFREIRE_MA
ENV ENV_BREJODEAREIA_MA=$ENV_BREJODEAREIA_MA
ENV ENV_OIAPOQUE_AP=$ENV_OIAPOQUE_AP
ENV ENV_TARRAFAS_CE=$ENV_TARRAFAS_CE
ENV ENV_SALVATERRA_PA=$ENV_SALVATERRA_PA
ENV ENV_LAGOADOOURO_PE=$ENV_LAGOADOOURO_PE

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

# Exponha a porta 8080
EXPOSE 8080

# Comando para iniciar o script de inicialização
CMD ["poetry", "run", "python", "app.py"]
