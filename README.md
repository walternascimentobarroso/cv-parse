# Doc-to-Text API – Development Environment

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=walternascimentobarroso_cv-parse&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=walternascimentobarroso_cv-parse)

This repository contains a small Doc-to-Text API and an improved development environment focused on fast onboarding and simple workflows.

## Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python package/dependency manager)
- Docker and Docker Compose

## Getting started

From the repo root:

```bash
cp .env.example .env
make install
make up
```

This installs dependencies with uv and starts the API and MongoDB. The API is available at `http://localhost:8000`.

## Makefile commands

- `make install` – Install dependencies from `pyproject.toml` / `uv.lock`
- `make up` – Start services with Docker Compose
- `make down` – Stop and remove containers
- `make logs` – Follow service logs
- `make run` – Run the app locally with uv
- `make test` – Run tests
- `make lint` – Run Ruff

## Environment configuration

Environment variables are defined in `.env` (not committed) with `.env.example` as the template. Both the app and Docker Compose read from `.env` so configuration is consistent.

See `specs/002-dev-env-tooling/quickstart.md` and `specs/002-dev-env-tooling/contracts/env.md` for details.

## Debug (VS Code / Cursor)

O projeto está configurado para debug da API FastAPI e dos testes com pytest. Use o passo a passo abaixo para ativar e usar o debug no futuro.

**Em qualquer modo de debug da API (local ou Docker), a API continua acessível em http://localhost:8000** — o debugpy usa só a porta 5678 para o IDE se conectar; o uvicorn segue na 8000.

### 1. Pré-requisitos

- **Python**: extensão Python (ou Pylance) instalada no editor.
- **Dependências**: ambiente criado com `make install` (ou `uv sync`).
- **MongoDB** (só para debug da API): serviços em execução com `make up`, para a API conectar ao banco.

### 2. Interpretador Python

O debugger usa o interpretador do ambiente virtual do projeto:

1. Abra a paleta de comandos: `Cmd+Shift+P` (macOS) ou `Ctrl+Shift+P` (Windows/Linux).
2. Procure por **Python: Select Interpreter**.
3. Selecione o interpretador do `.venv` do projeto (ex.: `./.venv/bin/python` ou o que o uv tiver criado).

Se o `.venv` não aparecer, rode `make install` na raiz do repositório e tente de novo.

### 3. Variáveis de ambiente para debug da API

Quando você roda a **API no seu machine** (via debug), ela precisa falar com o MongoDB. Com `make up`, o MongoDB fica em Docker e fica acessível em `localhost:27017`.

No seu `.env`, use:

```bash
MONGODB_URI=mongodb://localhost:27017
```

Assim a API em debug na sua máquina consegue conectar ao MongoDB do Docker. (Quando a API roda dentro do Docker, o Compose usa `mongodb:27017`; para debug local, use `localhost:27017`.)

### 4. Como iniciar o debug

1. Abra o painel **Run and Debug**: ícone de “play com inseto” na barra lateral ou `Cmd+Shift+D` / `Ctrl+Shift+D`.
2. No dropdown no topo do painel, escolha uma das configurações:
   - **FastAPI (debug)** – sobe a API com o debugger na sua máquina (recomendado para colocar breakpoints na API).
   - **FastAPI (debug + reload)** – mesma coisa, com reload automático ao salvar (o reload pode desconectar o debugger por um instante).
   - **FastAPI (attach to Docker)** – conecta o debugger à API rodando **dentro do Docker** (veja [Debug com a API no Docker](#6-debug-com-a-api-no-docker) abaixo).
   - **Pytest: current file** – roda e debuga só o arquivo de teste aberto.
   - **Pytest: all** – roda e debuga todos os testes em `tests/`.
3. Pressione **F5** (ou o botão verde “Start Debugging”) para iniciar.

### 5. Uso no dia a dia

- **Breakpoints**: clique na margem esquerda da linha (ou use o menu de contexto) para colocar um breakpoint.
- **API**: após iniciar **FastAPI (debug)**, a API fica em `http://localhost:8000`. Faça requisições (navegador, curl, Postman, etc.) e o debugger para nos breakpoints.
- **Testes**: abra um arquivo em `tests/`, escolha **Pytest: current file** e F5 para debugar só aquele arquivo; ou use **Pytest: all** para debugar a suíte inteira.

### 6. Debug com a API no Docker

Para debugar a API **rodando dentro do container** (com debugpy em modo “listen”):

1. No `.env`, defina `DEBUGPY=1` (ou exporte no terminal: `export DEBUGPY=1`).
2. **Reconstrua a imagem** para o container ter o `debugpy`: `docker compose build api` (ou `make recreate`).
3. Suba os serviços: `make up` (ou `docker compose up -d`).
4. No editor: **Run and Debug** → **FastAPI (attach to Docker)** → **F5**.
5. O debugger conecta na porta **5678**. A API continua em **http://localhost:8000** — use esse endereço para requisições e breakpoints.

O **Dockerfile** instala o `debugpy` via `uv sync`. O **docker-compose** expõe a porta **5678** (debugger) e a **8000** (API). Com `DEBUGPY=1`, o entrypoint inicia com `debugpy --listen 0.0.0.0:5678` e o uvicorn segue na 8000.

**Se http://localhost:8000 não abrir** com o debug ativado no Docker: confira se o container está de pé (`docker compose ps` e `docker compose logs api`). Se o container cair ou der erro de módulo, reconstrua: `docker compose build api` e `docker compose up -d`. Garanta que não há outro processo usando a porta 8000.

### 7. Resumo rápido (para reativar o debug depois)

**API na sua máquina (sem Docker):**

1. `make install` (se ainda não tiver feito).
2. `make up` (só MongoDB; se for debugar a API).
3. `.env` com `MONGODB_URI=mongodb://localhost:27017` para debug local da API.
4. **Python: Select Interpreter** → escolher o `.venv` do projeto.
5. **Run and Debug** → **FastAPI (debug)** ou **Pytest: current file** / **Pytest: all** → **F5**.

**API dentro do Docker:**

1. No `.env`: `DEBUGPY=1`.
2. `make up`.
3. **Run and Debug** → **FastAPI (attach to Docker)** → **F5**.

