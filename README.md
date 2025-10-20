# 📊 LUB - Sistema de Análise Financeira

Bem-vindo ao LUB! Este guia irá ajudá-lo a configurar e executar o projeto localmente.

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- **Python 3.10** - [Download aqui](https://www.python.org/downloads/)
- **Node.js** (versão 16 ou superior) - [Download aqui](https://nodejs.org/)
- **Yarn** - [Instruções de instalação](https://yarnpkg.com/getting-started/install)
- **Conda** (opcional, mas recomendado para gerenciamento de ambientes) - [Download Anaconda](https://www.anaconda.com/download)

## 🚀 Instalação e Configuração

### 1️⃣ Configuração do Backend

#### Passo 1: Criar Ambiente Virtual

```bash
# Se você usa Conda (recomendado)
conda create -n myenv python=3.10

# Se você usa venv (alternativa)
python3.10 -m venv myenv
```

#### Passo 2: Ativar o Ambiente Virtual

```bash
# No Conda
conda activate myenv

# No venv (Windows)
myenv\Scripts\activate

# No venv (Linux/Mac)
source myenv/bin/activate
```

#### Passo 3: Instalar Dependências do Backend

```bash
# Navegue até a pasta do backend
cd backend

# Instale as dependências
pip install -r requirements.txt
```

#### Passo 4: Executar o Backend

```bash
# Certifique-se de estar na pasta backend
python run.py
```

✅ **O backend estará rodando em:** `http://127.0.0.1:5000/api/`

Você pode testar acessando este endereço no navegador ou usando ferramentas como Postman.

---

### 2️⃣ Configuração do Frontend

#### Passo 1: Instalar Dependências do Frontend

```bash
# Abra um novo terminal (mantenha o backend rodando)
# Navegue até a pasta do frontend
cd frontend

# Instale as dependências com Yarn
yarn
```

Este comando irá instalar todos os pacotes Node.js necessários (pasta `node_modules`).

#### Passo 2: Executar o Frontend em Modo de Desenvolvimento

```bash
# Ainda na pasta frontend
yarn dev
```

✅ **O frontend estará disponível em:** `http://localhost:3000`

Abra este endereço no seu navegador para visualizar a aplicação.

---

## 🔧 Comandos Úteis

### Backend

```bash
# Parar o servidor: Ctrl + C

# Verificar versão do Python
python --version

# Atualizar dependências
pip install -r requirements.txt --upgrade
```

### Frontend

```bash
# Parar o servidor: Ctrl + C

# Build de produção
yarn build

# Iniciar em modo de produção
yarn start

# Limpar cache
yarn cache clean
```

---

## 📝 Estrutura do Projeto

```
lub/
├── backend/           # API e lógica de negócio (Python/Flask)
│   ├── app/          # Código principal da aplicação
│   ├── config.py     # Configurações
│   ├── run.py        # Arquivo principal para executar o backend
│   └── requirements.txt  # Dependências Python
│
└── frontend/         # Interface do usuário (Next.js/React)
    ├── app/          # Páginas da aplicação
    ├── components/   # Componentes reutilizáveis
    ├── __api__/      # Serviços de API
    └── package.json  # Dependências Node.js
```

---

## ⚠️ Solução de Problemas Comuns

### Erro: "Python não encontrado"
- Verifique se o Python 3.10 está instalado: `python --version`
- Adicione o Python ao PATH do sistema

### Erro: "pip não é reconhecido"
- Reinstale o Python e marque a opção "Add to PATH" durante a instalação

### Erro: "yarn não é reconhecido"
- Instale o Yarn globalmente: `npm install -g yarn`

### Erro: "Porta já em uso"
- Backend: Altere a porta no arquivo de configuração ou finalize o processo usando a porta 5000
- Frontend: Altere a porta no `package.json` ou finalize o processo usando a porta 3000

### Erro ao instalar dependências
- Limpe o cache: `pip cache purge` (Backend) ou `yarn cache clean` (Frontend)
- Delete as pastas `__pycache__` (Backend) e `node_modules` (Frontend) e reinstale

---

## 🌐 Deploy em Produção

Para fazer o deploy da aplicação em produção:

### Backend
```bash
cd backend
# Configure as variáveis de ambiente conforme necessário
# Use gunicorn ou outro servidor WSGI
gunicorn -c gunicorn.conf.py run:app
```

### Frontend
```bash
cd frontend
# Crie o build de produção
yarn build

# Execute em produção
yarn start
```

---

## 📧 Suporte

Se encontrar problemas ou tiver dúvidas, verifique:
- A documentação na pasta `frontend/docs/`
- Os logs de erro no console
- As configurações de ambiente

---

## 📄 Licença

Este projeto é privado e de uso interno.

---

**Última atualização:** Outubro 2025

**Versão Python:** 3.10  
**Versão Node.js:** 16+

