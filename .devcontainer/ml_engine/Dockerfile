# ----------------------------------------------------
# 1. Base común (entorno de ejecución compartido)
# ----------------------------------------------------
FROM python:3.11-slim AS base

WORKDIR /app

# Dependencias del sistema requeridas por LightGBM (OpenMP) y utilidades de red/DB
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias fijadas del motor de ML
# COPY apps/ml_engine/requirements.txt /tmp/requirements.txt
# RUN pip install --no-cache-dir --upgrade pip \
#     && pip install --no-cache-dir -r /tmp/requirements.txt

# ----------------------------------------------------
# 2. Target DEVELOPMENT: para VS Code Dev Containers
# ----------------------------------------------------
FROM base AS development

# Utilidades necesarias para vscode-server, terminal integrada y control de versiones
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    procps \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Configuración de usuario no-root con UID/GID 1000 estándar de Linux/WSL
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=1000

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

USER $USERNAME

# Garantiza que los binarios instalados por pip estén accesibles globalmente en la terminal
ENV PATH="/home/vscode/.local/bin:${PATH}"

# ----------------------------------------------------
# 3. Target PRODUCTION: imagen final autocontenida
# ----------------------------------------------------
FROM base AS production

COPY apps/ml_engine/ /app/apps/ml_engine/
RUN pip install --no-cache-dir -e /app/apps/ml_engine

USER 1000
#CMD ["python", "-m", "prescriptai_ml.train"]