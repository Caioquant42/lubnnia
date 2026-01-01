# OPLAB API Methods Overview

This document provides a comprehensive overview of all available methods from the OPLAB API v3, based on the OpenAPI specification.

## Table of Contents

1. [Introduction](#introduction)
2. [Authentication](#authentication)
3. [Implemented Endpoints](#implemented-endpoints)
4. [Market Endpoints](#market-endpoints)
5. [Domain Endpoints](#domain-endpoints)
6. [Summary Table](#summary-table)

---

## Introduction

The OPLAB REST API provides access to market data, options information, portfolio management, and trading functionality. The API is divided into two main categories:

- **Market**: Market data including quotes, options, stocks, interest rates, historical data, and statistics
- **Domain**: User-related data including portfolios, positions, orders, strategies, watchlists, robots, and notifications

**Base URL:** `https://api.oplab.com.br/v3`

**API Version:** 3.0

---

## Authentication

All API requests require authentication using an access token. The token can be provided in two ways:

1. **HTTP Header** (Recommended):
   ```
   Access-Token: {your-access-token}
   ```

2. **Query Parameter**:
   ```
   ?access_token={your-access-token}
   ```

Access tokens can be obtained from:
- OpLab website: https://go.oplab.com.br/api
- Authentication endpoint: `POST /domain/users/authenticate`

### Error Codes

- `400` - Bad Request: Invalid request parameters
- `401` - Unauthorized: Invalid or missing access token
- `402` - Payment Required: Subscription expired
- `403` - Forbidden: Plan doesn't allow access to this resource
- `404` - Not Found: Route not found
- `412` - Precondition Failed: Action requirements not met
- `422` - Unprocessable Entity: Processing failed
- `429` - Too Many Requests: Rate limit exceeded
- `500` - Internal Server Error: Server error
- `503` - Service Unavailable: Service temporarily unavailable

---

## Implemented Endpoints

The following endpoints are currently implemented in `backend/app/utils/collar.py`:

### GET `/market/interest_rates/{id}`

**Function:** `fetch_interest_rate(rate_id: str) -> Optional[Dict]`

**Summary:** Consultar taxa de juros

**Description:** Obtém os dados da taxa de juros especificada

**Parameters:**
- `rate_id` (path, string) - **Required** - Interest rate ID ('CETIP' or 'SELIC')

**Usage in collar.py:**
- Used to fetch SELIC rate for collar strategy calculations
- Called in `save_to_json()` function to get risk-free rate for CDI relative return calculations
- Returns interest rate value used in annual return calculations

**Example:**
```python
selic_data = fetch_interest_rate('SELIC')
selic_rate = selic_data['value'] if selic_data else 14.15
```

**Response Schema:**
```json
{
  "uid": "SELIC",
  "name": "Taxa Selic",
  "value": 3.4000915787165464,
  "updated_at": "2021-05-06T22:12:47.741Z"
}
```

**Implementation Location:** `backend/app/utils/collar.py:32-52`

---

### GET `/market/options/{symbol}`

**Function:** `fetch_option_data(underlying_symbols, max_retries=3, delay=5)`

**Summary:** Listar opções de um ativo

**Description:** Obtém uma lista com todas as opções de um determinado ativo

**Parameters:**
- `symbol` (path, string) - **Required** - Stock symbol (e.g., "PETR4", "VALE3")

**Usage in collar.py:**
- Fetches all options (CALL and PUT) for a list of underlying symbols
- Used in `main()` function to get raw option data
- Adds `parent_symbol` field to each option for tracking
- Implements retry logic with configurable max retries and delay
- Returns list of all options across all provided symbols

**Example:**
```python
underlying = ["PETR4", "VALE3", "BOVA11"]
raw_data = fetch_option_data(underlying)
```

**Response:** Array of option objects with fields including:
- `symbol`, `category` (CALL/PUT), `strike`, `due_date`, `days_to_maturity`
- `bid`, `ask`, `close`, `open`, `high`, `low`
- `volume`, `financial_volume`, `spot_price`
- `parent_symbol` (added by implementation)

**Implementation Location:** `backend/app/utils/collar.py:99-123`

---

### GET `/market/stocks/{symbol}`

**Function:** `fetch_underlying_data(underlying_symbols, max_retries=3, delay=5)`

**Summary:** Consultar uma ação

**Description:** Obtém um objeto com os detalhes de uma determiada ação. Além do schema de resposta abaixo, o retorno irá conter os atributos do parâmetro `with_financials`

**Parameters:**
- `symbol` (path, string) - **Required** - Stock symbol (e.g., "PETR4", "VALE3")
- `with_financials` (query, string) - Optional - Additional fields to include

**Usage in collar.py:**
- Fetches underlying stock data for collar strategy calculations
- Used to get spot prices (`ask` field) for option metrics calculations
- Filters response to include only essential fields
- Implements retry logic with configurable max retries and delay
- Returns list of stock data objects

**Example:**
```python
underlying = ["PETR4", "VALE3", "BOVA11"]
underlying_data = fetch_underlying_data(underlying)
```

**Response Fields Used:**
- `symbol`, `type`, `name`
- `open`, `high`, `low`, `close`
- `volume`, `financial_volume`, `trades`
- `bid`, `ask` (used as spot_price)
- `category`, `contract_size`
- `created_at`, `updated_at`
- `parent_symbol` (added by implementation)

**Implementation Location:** `backend/app/utils/collar.py:54-97`

**Note:** The implementation filters the full API response to only include the fields listed above, adding `parent_symbol` for tracking purposes.

---


## Market Endpoints

Market endpoints provide access to real-time and historical market data.

### Ações

### GET `/market/stocks`

**Status:** ❌ Not Implemented

**Summary:** Listar ações que possuem opções

**Description:** Obtém uma lista com todas as ações que possuem opções listadas

**Tags:** Ações

**Parameters:**

- **rank_by** (query, string) - Optional (default: `volume`) - Options: `symbol, type, name, open, high, low, close, volume, financial_volume, trades, bid, ask, category, contract_size, created_at, updated_at, variation, ewma_1y_max, ewma_1y_min, ewma_1y_percentile, ewma_1y_rank, ewma_current, has_options, iv_1y_max, iv_1y_min, iv_1y_percentile, iv_1y_rank, iv_current, middle_term_trend, semi_return_1y, short_term_trend, stdv_1y, stdv_5d, beta_ibov, due_date, maturity_type, parent_symbol, spot_price, strike, garch11_1y, isin, cnpj, correl_ibov, m9_m21, entropy, oplab_score, security_category, polynomials_2, polynomials_3, long_name, sector, time`
  Atributo para ordenação da lista. O parâmetro é case sensitive, insira o nome do atributo exatamente como está na lista enum

- **sort** (query, string) - Optional (default: `asc`) - Options: `asc, desc`
  Ordenação da lista. O parâmetro é case sensitive, insira o nome do atributo exatamente como está na lista enum

- **limit** (query, integer) - Optional (default: `20`)
  Quantidade máxima de itens na lista

- **financial_volume_start** (query, integer) - Optional
  Volume financeiro mínimo

**Responses:**

- `200`: OK
- `204`: Sem conteúdo
- `401`: Não autorizado
- `403`: Acesso negado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/market/stocks?rank_by={rank_by}&sort={sort}&limit={limit}&financial_volume_start={financial_volume_start}' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/market/stocks/all`

**Status:** ❌ Not Implemented

**Summary:** Listar todas as ações

**Description:** Obtém uma lista com todas as ações negociadas na B3

**Tags:** Ações

**Parameters:**

- **page** (query, integer) - Optional (default: `1`)
  Número da página

- **per** (query, integer) - Optional (default: `20`)
  Quantidade de itens por página

- **rank_by** (query, string) - Optional (default: `symbol`) - Options: `symbol, type, name, open, high, low, close, volume, financial_volume, trades, bid, ask, category, contract_size, created_at, updated_at, variation, ewma_1y_max, ewma_1y_min, ewma_1y_percentile, ewma_1y_rank, ewma_current, has_options, iv_1y_max, iv_1y_min, iv_1y_percentile, iv_1y_rank, iv_current, middle_term_trend, semi_return_1y, short_term_trend, stdv_1y, stdv_5d, beta_ibov, due_date, maturity_type, parent_symbol, spot_price, strike, garch11_1y, isin, cnpj, correl_ibov, m9_m21, entropy, oplab_score, security_category, polynomials_2, polynomials_3, long_name, sector, time`
  Atributo para ordenação da lista. O parâmetro é case sensitive, insira o nome do atributo exatamente como está na lista enum

- **sort** (query, string) - Optional (default: `asc`) - Options: `asc, desc`
  Ordenação da lista. O parâmetro é case sensitive, insira o nome do atributo exatamente como está na lista enum

- **financial_volume_start** (query, integer) - Optional
  Volume financeiro mínimo

**Responses:**

- `200`: OK
- `204`: Sem conteúdo
- `401`: Não autorizado
- `403`: Acesso negado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/market/stocks/all?page={page}&per={per}&rank_by={rank_by}&sort={sort}&financial_volume_start={financial_volume_start}' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/market/stocks/{symbol}`

**Status:** ✅ **IMPLEMENTED**

**Summary:** Consultar uma ação

**Description:** Obtém um objeto com os detalhes de uma determiada ação. Além do schema de resposta abaixo, o retorno irá conter os atributos do parâmetro `with_financials`

**Tags:** Ações

**Parameters:**

- **symbol** (path, string) - **Required**
  Código de negociação do ativo alvo

- **with_financials** (query, string) - Optional - Options: `sector, name, cvmCode, currency, currencyScale, dre, bpp, bpa, dfc, stocks, close, dividends, fundamentals, cnpj`
  Atributos para adicionar no retorno separados por vírgula. O parâmetro é case sensitive, insira o nome do atributo exatamente como está na lista enum

**Responses:**

- `200`: OK
- `204`: Sem conteúdo
- `401`: Não autorizado
- `403`: Acesso negado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/market/stocks/{symbol}?with_financials={with_financials}' \
  -H 'Access-Token: {access-token}'
```

---

### Bolsas de Valores

### GET `/market/exchanges`

**Status:** ❌ Not Implemented

**Summary:** Listar de bolsas de valores

**Description:** Obtém uma lista com as informações das bolsas de valores no Brasil

**Tags:** Bolsas de Valores

**Responses:**

- `200`: OK
- `204`: Sem conteúdo
- `401`: Não autorizado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/market/exchanges' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/market/exchanges/{uid}`

**Status:** ❌ Not Implemented

**Summary:** Consultar bolsa de valores

**Description:** Obtém os dados da bolsa de valores especificada

**Tags:** Bolsas de Valores

**Parameters:**

- **uid** (path, string) - **Required**
  UID da bolsa

**Responses:**

- `200`: OK
- `204`: Sem conteúdo
- `401`: Não autorizado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/market/exchanges/{uid}' \
  -H 'Access-Token: {access-token}'
```

---

### Dados Históricos

### GET `/market/historical/{symbol}/{resolution}`

**Status:** ❌ Not Implemented

**Summary:** Consultar dados históricos de um instrumento

**Description:** Obtém um objeto com a série histórica de um determinado instrumento no período especificado

**Tags:** Dados Históricos

**Parameters:**

- **symbol** (path, string) - **Required**
  Código de negociação do instrumento

- **resolution** (path, string) - **Required** (default: `1d`)
  Tempo de intervalo entre os dados contendo um número e uma letra. As letras reconhecidas são: h = hora, d = dia, w = semana, m = mês, y = ano; caso não seja informada nenhuma letra, considera-se minuto

- **from** (query, string) - **Required**
  Data de início da consulta

- **to** (query, string) - **Required**
  Data de fim da consulta

- **amount** (query, integer) - Optional
  Quantidade de itens de acordo com o período (hora, dia, semana, mês ou ano)

- **raw** (query, boolean) - Optional
  Indica se deve ignorar os dados financeiros, trazendo valores zerados

- **smooth** (query, boolean) - Optional
  Indica se deve preencher valores de `close` zerados com o valor do dia anterior

- **df** (query, string) - Optional (default: `timestamp`) - Options: `timestamp, iso`
  Formatação da data. O parâmetro é case sensitive, insira o nome do atributo exatamente como está na lista enum

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/market/historical/{symbol}/{resolution}?from={from}&to={to}&amount={amount}&raw={raw}&smooth={smooth}&df={df}' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/market/historical/options/{spot}/{from}/{to}`

**Status:** ❌ Not Implemented

**Summary:** Consultar histórico das opções de um ativo

**Description:** Obtém uma lista com as atualizações das opções do ativo especificado em um determinado período

**Tags:** Dados Históricos

**Parameters:**

- **spot** (path, string) - **Required**
  Código de negociação do ativo alvo

- **from** (path, string) - **Required**
  Data de início da consulta

- **to** (path, string) - **Required**
  Data de fim da consulta

- **symbol** (query, string) - Optional
  Código de negociação da opção a ser listada

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/market/historical/options/{spot}/{from}/{to}?symbol={symbol}' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/market/historical/instruments`

**Status:** ❌ Not Implemented

**Summary:** Consultar dados dos instrumentos em determinada data

**Description:** Obtém uma lista com dados dos instrumentos na data especificada

**Tags:** Dados Históricos

**Parameters:**

- **tickers** (query, string) - **Required**
  Código de negociação dos instrumentos separados por vírgula

- **date** (query, string) - **Required**
  Data da consulta

**Responses:**

- `200`: OK
- `204`: Sem conteúdo
- `400`: Requisição inválida
- `401`: Não autorizado
- `403`: Acesso negado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/market/historical/instruments?tickers={tickers}&date={date}' \
  -H 'Access-Token: {access-token}'
```

---

### Instrumentos

### GET `/market/quote`

**Status:** ❌ Not Implemented

**Summary:** Consultar cotações de uma lista de instrumentos

**Description:** Obtém uma lista com a cotação de um ou mais instrumentos

**Tags:** Instrumentos

**Parameters:**

- **tickers** (query, string) - **Required**
  Código de negociação dos instrumentos separados por vírgula

**Responses:**

- `200`: OK
- `204`: Sem conteúdo
- `400`: Requisição inválida
- `401`: Não autorizado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/market/quote?tickers={tickers}' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/market/instruments/search`

**Status:** ❌ Not Implemented

**Summary:** Listar instrumentos

**Description:** Obtém uma lista de instrumentos

**Tags:** Instrumentos

**Parameters:**

- **expr** (query, string) - **Required**
  Códigos de negociação ou nomes da companhia para pesquisa separados por vírgula, podem ser informados valores parciais

- **limit** (query, number) - Optional (default: `10`)
  Quantidade máxima de itens na lista

- **type** (query, string) - Optional (default: `STOCK,OPTION`) - Options: `STOCK, OPTION, INDEX, REAL_ESTATE_FUND, INDICATOR, INTEREST_RATE, BOND`
  Tipos de instrumento para pesquisa separados por vírugla

- **has_options** (query, boolean) - Optional
  Indica se o instrumento deve ter opções listadas na B3

- **category** (query, string) - Optional - Options: `CALL, PUT`
  Tipo de opção a ser filtrada, só é considerado se o type for `OPTION`

- **add_info** (query, boolean) - Optional
  Indica se o retorno deve incluir as informações adicionais, que são: `close`, `variation`, `volume`, `iv_current`, `iv_1y_rank` e `iv_1y_percentile`

**Responses:**

- `200`: OK
- `204`: Sem conteúdo
- `400`: Requisição inválida
- `401`: Não autorizado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/market/instruments/search?expr={expr}&limit={limit}&type={type}&has_options={has_options}&category={category}&add_info={add_info}' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/market/instruments/series/{symbol}`

**Status:** ❌ Not Implemented

**Summary:** Listar séries de opções de um instrumento

**Description:** Obtém um objeto com os dados do instrumento e todas as séries de opções

**Tags:** Instrumentos

**Parameters:**

- **symbol** (path, string) - **Required**
  Código de negociação do instrumento

- **bs** (query, boolean) - Optional
  Um parâmetro booleano para ativar ou desativar o black and scholes. Se fornecido, `irate` também deve ser especificado.

- **irate** (query, number) - Optional
  Um valor percentual necessário que representa a taxa de juros usada quando `bs` é fornecido.

**Responses:**

- `200`: OK
- `204`: Sem conteúdo
- `400`: Requisição inválida
- `401`: Não autorizado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/market/instruments/series/{symbol}' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/market/instruments/{symbol}`

**Status:** ❌ Not Implemented

**Summary:** Consultar um instrumento

**Description:** Obtém um objeto com os dados do instrumento especificado

**Tags:** Instrumentos

**Parameters:**

- **symbol** (path, string) - **Required**
  Código de negociação do instrumento

**Responses:**

- `200`: OK
- `204`: Sem conteúdo
- `400`: Requisição inválida
- `401`: Não autorizado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/market/instruments/{symbol}' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/market/instruments`

**Status:** ❌ Not Implemented

**Summary:** Consultar detalhes de uma lista de instrumentos

**Description:** Obtém uma lista com os detalhes de um ou mais instrumentos

**Tags:** Instrumentos

**Parameters:**

- **tickers** (query, string) - **Required**
  Código de negociação dos instrumentos separados por vírgula

**Responses:**

- `200`: OK
- `204`: Sem conteúdo
- `400`: Requisição inválida
- `401`: Não autorizado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/market/instruments?tickers={tickers}' \
  -H 'Access-Token: {access-token}'
```

---

### Mercado

### GET `/market/status`

**Status:** ❌ Not Implemented

**Summary:** Consultar status do mercado

**Description:** Obtém um objeto com o status atual do mercado, sendo o retorno uma das siglas abaixo
- `P` = Pré abertura
- `A` = Abertura (sessão normal)
- `PN` = Pré fechamento
- `N` = Fechamento
- `E` = Pré abertura do after
- `R` = Abertura After
- `NE` = Fechamento do after
- `F` = Final

**Tags:** Mercado

**Responses:**

- `200`: OK
- `401`: Não autorizado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/market/status' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/market/companies`

**Status:** ❌ Not Implemented

**Summary:** Consultar uma lista de companhias

**Description:** Obtém uma lista com uma ou mais companhias. Além do schema de resposta abaixo, o retorno irá conter os atributos do parâmetro `includes`

**Tags:** Mercado

**Parameters:**

- **symbols** (query, string) - **Required**
  Códigos de negociação das ações separados por vírgula

- **includes** (query, string) - Optional - Options: `type, name, open, high, low, close, volume, financial_volume, trades, bid, ask, category, exchange_id, created_at, updated_at, variation, has_options, middle_term_trend, semi_return_1y, short_term_trend, stdv_1y, stdv_5d, beta_ibov, due_date, maturity_type, parent_symbol, spot_price, strike, ewma_1y_max, ewma_1y_min, ewma_1y_percentile, ewma_1y_rank, ewma_current, garch11_1y, isin, correl_ibov, m9_m21, entropy, oplab_score, security_category, sector, cvmCode, currency, currencyScale, dre, bpp, bpa, dfc, stocks, close, dividends, fundamentals`
  Atributos para adicionar no retorno separados por vírgula. O parâmetro é case sensitive, insira o nome do atributo exatamente como está na lista enum

**Responses:**

- `200`: OK
- `204`: Sem conteúdo
- `400`: Requisição inválida
- `401`: Não autorizado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/market/companies?symbols={symbols}&includes={includes}' \
  -H 'Access-Token: {access-token}'
```

---

### Opções

### GET `/market/options/{symbol}`

**Status:** ✅ **IMPLEMENTED**

**Summary:** Listar opções de um ativo

**Description:** Obtém uma lista com todas as opções de um determinado ativo

**Tags:** Opções

**Parameters:**

- **symbol** (path, string) - **Required**
  Código da ação da companhia

**Responses:**

- `200`: OK
- `204`: Sem conteúdo
- `400`: Requisição inválida
- `401`: Não autorizado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/market/options/{symbol}' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/market/options/details/{symbol}`

**Status:** ❌ Not Implemented

**Summary:** Consultar uma opção

**Description:** Obtém um objeto com os detalhes de uma determinada opção

**Tags:** Opções

**Parameters:**

- **symbol** (path, string) - **Required**
  Código de negociação da opção

**Responses:**

- `200`: OK
- `204`: Sem conteúdo
- `400`: Requisição inválida
- `401`: Não autorizado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/market/options/details/{symbol}' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/market/options/strategies/covered`

**Status:** ❌ Not Implemented

**Summary:** Listar opções para estratégias cobertas

**Description:** Obtém uma lista das opções com strike menor ou igual ao preço de um ou mais ativos

**Tags:** Opções

**Parameters:**

- **underlying** (query, string) - Optional
  Códigos das ações das companhias separados por vírgula

**Responses:**

- `200`: OK
- `204`: Sem conteúdo
- `401`: Não autorizado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/market/options/strategies/covered?underlying={underlying}' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/market/options/bs`

**Status:** ❌ Not Implemented

**Summary:** Consultar Black-Scholes de uma opção

**Description:** Obtém um objeto com o preço teórico, as gregas, a volatilidade implícita e a margem teórica de uma determinada opção

**Tags:** Opções

**Parameters:**

- **symbol** (query, string) - **Required**
  Código de negociação da opção

- **irate** (query, number) - **Required**
  Valor da taxa de juros (%)

- **type** (query, string) - Optional - Options: `CALL, PUT`
  Tipo de opção. Obrigatório se o `symbol` não for informado

- **spotprice** (query, number) - Optional
  Preço atual do ativo alvo

- **strike** (query, number) - Optional
  Valor do strike da opção. Obrigatório se o código de negociação for de uma ação

- **premium** (query, number) - Optional
  Valor do prêmio da opção

- **dtm** (query, integer) - Optional
  Dias faltantes para o vencimento da opção

- **vol** (query, number) - Optional
  Volatilidade implícita da opção

- **duedate** (query, string) - Optional
  Data de vencimento da opção. Obrigatório se o código de negociação for de uma ação

- **amount** (query, integer) - Optional
  Quantidade de ativos

**Responses:**

- `200`: OK
- `204`: Sem conteúdo
- `400`: Requisição inválida
- `401`: Não autorizado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/market/options/bs?symbol={symbol}&irate={irate}&type={type}&spotprice={spot_price}&strike={strike}&premium={premium}&dtm={dtm}&vol={vol}&duedate={due_date}&amount={amount}' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/market/options/powders`

**Status:** ❌ Not Implemented

**Summary:** Listar principais pozinhos

**Description:** Obtém uma lista com os principais pozinhos

**Tags:** Opções

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/market/options/powders' \
  -H 'Access-Token: {access-token}'
```

---

### Rankings

### GET `/market/statistics/realtime/highest_options_volume`

**Status:** ❌ Not Implemented

**Summary:** Listar maiores volumes em opções

**Description:** Obtém uma lista com os ativos com maiores volumes financeiros negociados em opções

**Tags:** Rankings

**Parameters:**

- **order_by** (query, string) - Optional (default: `total`) - Options: `call, put, total`
  Propriedade pela qual a lista será ordenada (ordenação descrescente). O parâmetro é case sensitive, insira o nome do atributo exatamente como está na lista enum

- **limit** (query, integer) - Optional (default: `20`)
  Quantidade máxima de itens na lista

**Responses:**

- `200`: OK
- `204`: Sem conteúdo
- `401`: Não autorizado
- `403`: Acesso negado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/market/statistics/realtime/highest_options_volume?order_by={order_by}&limit={limit}' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/market/statistics/realtime/best_covered_options_rates/{type}`

**Status:** ❌ Not Implemented

**Summary:** Listar opções com as maiores taxas de lucro

**Description:** Obtém uma lista com as opções com as maiores taxas de lucro, considerando apenas opções PUT OTM e CALL ITM

**Tags:** Rankings

**Parameters:**

- **type** (path, string) - **Required** - Options: `CALL, PUT`
  Tipo da opção

- **limit** (query, integer) - Optional (default: `20`)
  Quantidade máxima de itens na lista

**Responses:**

- `200`: OK
- `204`: Sem conteúdo
- `401`: Não autorizado
- `403`: Acesso negado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/market/statistics/realtime/best_covered_options_rates/{type}?limit={limit}' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/market/statistics/realtime/highest_options_variation/{type}`

**Status:** ❌ Not Implemented

**Summary:** Listar opções com as maiores variações

**Description:** Obtém uma lista com as opções com as maiores variações de preço

**Tags:** Rankings

**Parameters:**

- **type** (path, string) - **Required** - Options: `CALL, PUT`
  Tipo da opção

- **limit** (query, integer) - Optional (default: `20`)
  Quantidade máxima de itens na lista

**Responses:**

- `200`: OK
- `204`: Sem conteúdo
- `401`: Não autorizado
- `403`: Acesso negado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/market/statistics/realtime/highest_options_variation/{type}?limit={limit}' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/market/statistics/ranking/m9_m21`

**Status:** ❌ Not Implemented

**Summary:** Listar opções com as maiores tendências de alta/baixa

**Description:** Obtém uma lista com as opções com as maiores tendências de alta ou de baixa, considerando a relação entre a média de 9 e 21 dias

**Tags:** Rankings

**Parameters:**

- **limit** (query, integer) - Optional (default: `20`)
  Quantidade máxima de itens na lista

- **sort** (query, string) - Optional (default: `asc`) - Options: `asc, desc`
  Ordenação da lista, determina se retornará as tendências de alta ou de baixa. O parâmetro é case sensitive, insira o nome do atributo exatamente como está na lista enum

- **financial_volume_start** (query, integer) - Optional
  Volume financeiro mínimo

- **days** (query, integer) - Optional (default: `3650`)
  Máximo de dias a partir da última atualização

**Responses:**

- `200`: OK
- `204`: Sem conteúdo
- `401`: Não autorizado
- `403`: Acesso negado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/market/statistics/ranking/m9_m21?limit={limit}&sort={sort}&financial_volume_start={financial_volume_start}&days={days}' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/market/statistics/ranking/correl_ibov`

**Status:** ❌ Not Implemented

**Summary:** Listar opções ordenadas pela correlação com IBOV

**Description:** Obtém uma lista com as opções com as maiores ou menores correlações com o IBOV

**Tags:** Rankings

**Parameters:**

- **limit** (query, integer) - Optional (default: `20`)
  Quantidade máxima de itens na lista

- **sort** (query, string) - Optional (default: `asc`) - Options: `asc, desc`
  Ordenação da lista, determina se retornará as maiores ou as menores correlações. O parâmetro é case sensitive, insira o nome do atributo exatamente como está na lista enum

- **financial_volume_start** (query, integer) - Optional
  Volume financeiro mínimo

- **days** (query, integer) - Optional (default: `3650`)
  Máximo de dias a partir da última atualização

**Responses:**

- `200`: OK
- `204`: Sem conteúdo
- `401`: Não autorizado
- `403`: Acesso negado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/market/statistics/ranking/correl_ibov?limit={limit}&sort={sort}&financial_volume_start={financial_volume_start}&days={days}' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/market/statistics/ranking/{attribute}`

**Status:** ❌ Not Implemented

**Summary:** Listar companhias ordenadas por um atributo fundamentalista

**Description:** Obtém uma lista com as companhias com os maiores ou menores índices do atributo fundamentalista especificado, podendo ser agrupado e retornar os setores com as maiores ou menores médias de índices do atributo fundamentalista especificado

**Tags:** Rankings

**Parameters:**

- **attribute** (path, string) - **Required** - Options: `date, cash_and_equivalents, ebit, earnings, market_cap, earnings_over_ebit, earnings_over_netrevenue, roic, roa, roe, gross_margin, ebit_margin, net_margin, interest_coverage_ratio, current_ratio, ev, ev_over_ebit, profit_per_share, price_over_profit_per_share, magic_formula`
  Atributo fundamentalista. O parâmetro é case sensitive, insira o nome do atributo exatamente como está na lista enum

- **group_by** (query, string) - Optional - Options: `sector`
  Agrupa a classificação pela propriedade informada. O parâmetro é case sensitive, insira o nome do atributo exatamente como está na lista enum

- **limit** (query, integer) - Optional (default: `20`)
  Quantidade máxima de itens na lista

- **sort** (query, string) - Optional (default: `asc`) - Options: `asc, desc`
  Ordenação da lista, determina se retornará os maiores ou menores índices. O parâmetro é case sensitive, insira o nome do atributo exatamente como está na lista enum

- **financial_volume_start** (query, integer) - Optional
  Volume financeiro mínimo

**Responses:**

- `200`: OK
- `204`: Sem conteúdo
- `400`: Requisição inválida
- `401`: Não autorizado
- `403`: Acesso negado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/market/statistics/ranking/{attribute}?group_by={group_by}&limit={limit}&sort={sort}&financial_volume_start={financial_volume_start}' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/market/statistics/ranking/oplab_score`

**Status:** ❌ Not Implemented

**Summary:** Listar ações ordenadas pelo OpLab score

**Description:** Obtém uma lista com as ações com os maiores ou menores OpLab scores, podendo ser agrupado e retornar os setores com as maiores ou menores médias do OpLab score

**Tags:** Rankings

**Parameters:**

- **score_start** (query, integer) - Optional
  OpLab score mínimo

- **financial_volume_start** (query, integer) - Optional
  Volume financeiro mínimo

- **group_by** (query, string) - Optional - Options: `sector`
  Agrupa a classificação pela propriedade informada. O parâmetro é case sensitive, insira o nome do atributo exatamente como está na lista enum

- **sort** (query, string) - Optional (default: `asc`) - Options: `asc, desc`
  Ordenação da lista, determina se retornará os maiores ou menores OpLab scores. O parâmetro é case sensitive, insira o nome do atributo exatamente como está na lista enum

- **limit** (query, integer) - Optional (default: `20`)
  Quantidade máxima de itens na lista

**Responses:**

- `200`: OK
- `204`: Sem conteúdo
- `401`: Não autorizado
- `403`: Acesso negado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/market/statistics/ranking/oplab_score?score_start={score_start}&financial_volume_start={financial_volume_start}&group_by={group_by}&sort={sort}&limit={limit}' \
  -H 'Access-Token: {access-token}'
```

---

### Taxas de Juros

### GET `/market/interest_rates`

**Status:** ❌ Not Implemented

**Summary:** Listar taxas de juros

**Description:** Obtém uma lista com todas as taxas de juros disponíveis

**Tags:** Taxas de Juros

**Responses:**

- `200`: OK
- `204`: Sem conteúdo
- `401`: Não autorizado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/market/interest_rates' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/market/interest_rates/{id}`

**Status:** ✅ **IMPLEMENTED**

**Summary:** Consultar taxa de juros

**Description:** Obtém os dados da taxa de juros especificada

**Tags:** Taxas de Juros

**Parameters:**

- **id** (path, string) - **Required**
  Sigla da taxa de juros

**Responses:**

- `200`: OK
- `204`: Sem conteúdo
- `401`: Não autorizado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/market/interest_rates/{id}' \
  -H 'Access-Token: {access-token}'
```

---


## Domain Endpoints

Domain endpoints provide access to user-specific data and portfolio management.

### Contas de Trade

### GET `/domain/trading_accounts`

**Status:** ❌ Not Implemented

**Summary:** Listar contas de trade

**Description:** Obtém uma lista com todas as contas de trade do usuário

**Tags:** Contas de Trade

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/trading_accounts' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/domain/trading_accounts/{id}`

**Status:** ❌ Not Implemented

**Summary:** Consultar conta de trade

**Description:** Obtém um objeto com os dados da conta de trade especificada

**Tags:** Contas de Trade

**Parameters:**

- **id** (path, integer) - **Required**
  ID da conta de trade

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/trading_accounts/{id}' \
  -H 'Access-Token: {access-token}'
```

---

### PUT `/domain/trading_accounts/{id}/cancel`

**Status:** ❌ Not Implemented

**Summary:** Cancelar conta de trade

**Description:** Cancela a conta de trade especificada

**Tags:** Contas de Trade

**Parameters:**

- **id** (path, integer) - **Required**
  ID da conta de trade

**Responses:**

- `200`: OK
- `204`: Sem conteúdo
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X PUT \
  'https://api.oplab.com.br/v3/domain/trading_accounts/{id}/cancel' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/domain/trading_accounts/{id}/pending_terms`

**Status:** ❌ Not Implemented

**Summary:** Listar termos pendentes da conta de trade

**Description:** Obtém uma lista com os termos de responsabilidade da corretora que o usuário ainda não aceitou

**Tags:** Contas de Trade

**Parameters:**

- **id** (path, integer) - **Required**
  ID da conta de trade

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/trading_accounts/{id}/pending_terms' \
  -H 'Access-Token: {access-token}'
```

---

### POST `/domain/trading_accounts/{trading_account_id}/agree/{term_id}`

**Status:** ❌ Not Implemented

**Summary:** Aceitar termo da corretora

**Description:** Aceita o termo de responsabilidade especificado

**Tags:** Contas de Trade

**Parameters:**

- **trading_account_id** (path, integer) - **Required**
  ID da conta de trade

- **term_id** (path, integer) - **Required**
  ID do termo

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado

**Example Request:**

```bash
curl -i -X POST \
  'https://api.oplab.com.br/v3/domain/trading_accounts/{trading_account_id}/agree/{term_id}' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/domain/trading_accounts/{trading_account_id}/events`

**Status:** ❌ Not Implemented

**Summary:** Listar eventos da conta de trade

**Description:** Obtém uma lista com os eventos da conta de trade especificada

**Tags:** Contas de Trade

**Parameters:**

- **trading_account_id** (path, integer) - **Required**
  ID da conta de trade

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/trading_accounts/{trading_account_id}/events' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/domain/trading_accounts/{trading_account_id}/events/{id}`

**Status:** ❌ Not Implemented

**Summary:** Consultar evento da conta de trade

**Description:** Obtém um objeto com os detalhes do evento especificado da conta de trade

**Tags:** Contas de Trade

**Parameters:**

- **trading_account_id** (path, integer) - **Required**
  ID da conta de trade

- **id** (path, integer) - **Required**
  ID do evento da conta de trade

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/trading_accounts/{trading_account_id}/events/{id}' \
  -H 'Access-Token: {access-token}'
```

---

### Corretoras

### GET `/domain/brokers`

**Status:** ❌ Not Implemented

**Summary:** Listar corretoras

**Description:** Obtém uma lista com todas as corretoras cadastradas

**Tags:** Corretoras

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/brokers' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/domain/brokers/{id}`

**Status:** ❌ Not Implemented

**Summary:** Consultar corretora

**Description:** Obtém um objeto com os dados da corretora especificada

**Tags:** Corretoras

**Parameters:**

- **id** (path, integer) - **Required**
  ID da corretora

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/domain/brokers/{id}' \
  -H 'Access-Token: {access-token}'
```

---

### POST `/domain/brokers/{id}/sign_up`

**Status:** ❌ Not Implemented

**Summary:** Cadastrar usuário na corretora

**Description:** Cadastra o usuário na corretora especificada, criando uma conta de trade

**Tags:** Corretoras

**Parameters:**

- **id** (path, integer) - **Required**
  ID da corretora

**Request Body:**

See OpenAPI spec for request body schema.

**Responses:**

- `201`: Criado
- `400`: Requisição inválida
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X POST \
  'https://api.oplab.com.br/v3/domain/brokers/{id}/sign_up'\
  -H 'Access-Token: {access-token}' \
  -H 'content-type: application/json' \
  -d '{
    "plan_id": 19,
    "pin": "2134"
  }'
```

---

### Estratégias

### GET `/domain/portfolios/{portfolio_id}/strategies`

**Status:** ❌ Not Implemented

**Summary:** Listar estratégias

**Description:** Obtém uma lista com todas as estratégias do portfólio especificado

**Tags:** Estratégias

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

- **status** (query, string) - Optional (default: `open`) - Options: `open, all`
  Status das posições da estratégia a serem listadas

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/strategies?status={status}' \
  -H 'Access-Token: {access-token}'
```

---

### POST `/domain/portfolios/{portfolio_id}/strategies`

**Status:** ❌ Not Implemented

**Summary:** Incluir estratégia

**Description:** Inclui uma estratégia no portfólio especificado

**Tags:** Estratégias

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

**Request Body:**

See OpenAPI spec for request body schema.

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X POST \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/strategies' \
  -H 'Access-Token: {access-token}' \
  -H 'content-type: application/json' \
  -d '{
    "name": "Venda coberta",
    "underlying": "ABEV3",
    "origin": "order_ticket",
    "positions":
    [
      {
        "symbol": "ABEV3",
        "amount": 100,
        "side": "BUY",
        "price": 17.08
      }
    ],
    "published_at": "2023-07-07",
    "expired_at": "2023-07-13",
    "short_description": "Teste",
    "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin porttitor ut nulla nec blandit. Vivamus eu enim et elit imperdiet ullamcorper nec id justo. Sed et vestibulum lorem, ut euismod ante. Sed eu elementum augue, eu egestas lectus. Nam enim quam, viverra eu quam et, lacinia vulputate sem. Pellentesque lacinia gravida placerat. Nullam erat purus, mattis non dui vel, ultricies malesuada arcu. Ut dictum neque eget nulla volutpat, ac maximus purus malesuada. Proin quis ligula semper, tincidunt odio et, aliquet nulla."
  }'
```

---

### GET `/domain/portfolios/{portfolio_id}/strategies/{id}`

**Status:** ❌ Not Implemented

**Summary:** Consultar estratégia

**Description:** Obtém um objeto com os dados da estratégia especificada

**Tags:** Estratégias

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

- **id** (path, integer) - **Required**
  ID da estratégia

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/strategies/{id}' \
  -H 'Access-Token: {access-token}'
```

---

### DELETE `/domain/portfolios/{portfolio_id}/strategies/{id}`

**Status:** ❌ Not Implemented

**Summary:** Remover estratégia

**Description:** Remove uma estratégia do portfólio especificado

**Tags:** Estratégias

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

- **id** (path, integer) - **Required**
  ID da estratégia

**Responses:**

- `204`: Sem conteúdo
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X DELETE \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/strategies/{id}' \
  -H 'Access-Token: {access-token}'
```

---

### PUT `/domain/portfolios/{portfolio_id}/strategies/{id}/rename`

**Status:** ❌ Not Implemented

**Summary:** Renomear estratégia

**Description:** Renomeia a estratégia especificada

**Tags:** Estratégias

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

- **id** (path, integer) - **Required**
  ID da estratégia

**Request Body:**

See OpenAPI spec for request body schema.

**Responses:**

- `200`: OK
- `400`: Requisição inválida
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X PUT \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/strategies/{id}/rename' \
  -H 'Access-Token: {access-token}' \
  -H 'content-type: application/json' \
  -d '{
    "name": "Estratégia renomeada"
  }'
```

---

### PUT `/domain/portfolios/{portfolio_id}/strategies/{id}/commit`

**Status:** ❌ Not Implemented

**Summary:** Consolidar estratégia

**Description:** Consolida e retorna uma lista com os dados das posições da estratégia especificada

**Tags:** Estratégias

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

- **id** (path, integer) - **Required**
  ID da estratégia

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X PUT \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/strategies/{id}/commit' \
  -H 'Access-Token: {access-token}'
```

---

### PUT `/domain/portfolios/{portfolio_id}/strategies/{id}/close`

**Status:** ❌ Not Implemented

**Summary:** Fechar estratégia

**Description:** Fecha as posições da estratégia especificada

**Tags:** Estratégias

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

- **id** (path, integer) - **Required**
  ID da estratégia

**Request Body:**

See OpenAPI spec for request body schema.

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X PUT \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/strategies/{id}/close' \
  -H 'Access-Token: {access-token}' \
  -H 'content-type: application/json' \
  -d '{
    "exercise":
    [
      41998,
      41999
    ]
  }'
```

---

### Notificações

### GET `/domain/notifications`

**Status:** ❌ Not Implemented

**Summary:** Listar notificações

**Description:** Obtém uma lista com todas as notificações recebidas do usuário

**Tags:** Notificações

**Parameters:**

- **page** (query, integer) - Optional
  Número da página da pesquisa

- **per** (query, integer) - Optional
  Quantidade de itens por página

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/notifications?page={page}&per={per}' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/domain/notifications/{id}`

**Status:** ❌ Not Implemented

**Summary:** Consultar notificação

**Description:** Obtém um objeto com os dados da notificação especificada

**Tags:** Notificações

**Parameters:**

- **id** (path, integer) - **Required**
  ID da notificação

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/notifications/{id}' \
  -H 'Access-Token: {access-token}'
```

---

### PUT `/domain/notifications/{id}`

**Status:** ❌ Not Implemented

**Summary:** Alterar notificação

**Description:** Altera os dados da notificação especificada

**Tags:** Notificações

**Parameters:**

- **id** (path, integer) - **Required**
  ID da notificação

**Request Body:**

See OpenAPI spec for request body schema.

**Responses:**

- `200`: OK
- `400`: Requisição inválida
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X PUT \
  'https://api.oplab.com.br/v3/domain/notifications/{id}' \
  -H 'Access-Token: {access-token}' \
  -H 'content-type: application/json' \
  -d '{
    "ack_at": "2021-07-19T17:59:45.667-03:00",
    "read_at": "2021-07-19T17:59:45.667-03:00",
    "deleted_at": null
  }'
```

---

### DELETE `/domain/notifications/{id}`

**Status:** ❌ Not Implemented

**Summary:** Remover notificação

**Description:** Remove os dados da notificação especificada

**Tags:** Notificações

**Parameters:**

- **id** (path, integer) - **Required**
  ID da notificação

**Responses:**

- `204`: Sem conteúdo
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X DELETE \
  'https://api.oplab.com.br/v3/domain/notifications/{id}' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/domain/notifications/unread`

**Status:** ❌ Not Implemented

**Summary:** Contar notificações não lidas

**Description:** Obtém a quantidade de notificações não lidas do usuário

**Tags:** Notificações

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/notifications/unread' \
  -H 'Access-Token: {access-token}'
```

---

### POST `/domain/notifications/read_all`

**Status:** ❌ Not Implemented

**Summary:** Marcar notificações como lidas

**Description:** Altera todas as notificações do usuário, marcando como lidas

**Tags:** Notificações

**Responses:**

- `204`: Sem conteúdo
- `401`: Não autorizado
- `403`: Acesso negado

**Example Request:**

```bash
curl -i -X POST \
  'https://api.oplab.com.br/v3/domain/notifications/read_all' \
  -H 'Access-Token: {access-token}'
```

---

### POST `/domain/notifications/delete_all`

**Status:** ❌ Not Implemented

**Summary:** Remover notificações

**Description:** Remove todas as notificações do usuário

**Tags:** Notificações

**Responses:**

- `204`: Sem conteúdo
- `401`: Não autorizado
- `403`: Acesso negado

**Example Request:**

```bash
curl -i -X POST \
  'https://api.oplab.com.br/v3/domain/notifications/delete_all' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/domain/notifications/preferences`

**Status:** ❌ Not Implemented

**Summary:** Consultar preferências

**Description:** Obtém uma lista com todas as preferências de notificações do usuário

**Tags:** Notificações

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/notifications/preferences' \
  -H 'Access-Token: {access-token}'
```

---

### POST `/domain/notifications/preferences`

**Status:** ❌ Not Implemented

**Summary:** Alterar preferências

**Description:** Altera as preferências de notificações do usuário

**Tags:** Notificações

**Request Body:**

See OpenAPI spec for request body schema.

**Responses:**

- `204`: Sem conteúdo
- `400`: Requisição inválida
- `401`: Não autorizado
- `403`: Acesso negado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X POST \
  'https://api.oplab.com.br/v3/domain/notifications/preferences' \
  -H 'Access-Token: {access-token}' \
  -H 'content-type: application/json' \
  -d '{
    "preferences":
    [
      {
        "channel_id": 1,
        "destination_mask": 10
      },
      {
        "channel_id": 2,
        "destination_mask": 111
      }
    ]
  }'
```

---

### Ordens

### GET `/domain/portfolios/{portfolio_id}/orders`

**Status:** ❌ Not Implemented

**Summary:** Listar ordens de um portfólio

**Description:** Obtém uma lista com as ordens do portfólio especificado

**Tags:** Ordens

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

- **from** (query, string) - Optional
  Data de início da consulta

- **to** (query, string) - Optional
  Data de fim da consulta

- **page** (query, integer) - Optional
  Número da página da pesquisa

- **per** (query, integer) - Optional
  Quantidade de itens por página

- **ticker** (query, string) - Optional
  Código do ativo das ordens a serem listadas, pode ser informado um valor parcial

- **origin** (query, string) - Optional - Options: `simulator, order_ticket, robot`
  Origem das ordens a serem listadas. Aceita mais de um valor, separando por vírgula

- **status** (query, string) - Optional - Options: `pending, filled, canceled, staged, created, partially_filled, rejected, expired, replaced, done_for_day, pending_cancel, stopped, suspended, pending_new, calculated, accepted_for_bidding, pending_replace`
  Status das ordens a serem listadas. Aceita mais de um valor, separando por vírgula. Obs: Quando o valor `partially_filled` é passado, as ordens canceladas ou expiradas que anteriormente foram executadas parcialmente serão retornadas

- **order_type** (query, string) - Optional - Options: `manual, market, limit, stop_limit`
  Tipo de ordens a serem listadas. Aceita mais de um valor, separando por vírgula

- **side** (query, string) - Optional - Options: `SELL, BUY`
  Lado das ordens a serem listadas. Aceita mais de um valor, separando por vírgula

- **show_position** (query, boolean) - Optional (default: `True`)
  Determina se as ordens devem incluir as informações da posição

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/orders?from={from}&to={to}&page={page}&per={per}&ticker={ticker}&origin={origin}&status={status}&order_type={order_type}&side={side}&show_position={show_position}' \
  -H 'Access-Token: {access-token}'
```

---

### POST `/domain/portfolios/{portfolio_id}/orders`

**Status:** ❌ Not Implemented

**Summary:** Incluir ordem em um portfólio

**Description:** Inclui uma ordem no portfólio especificado

**Tags:** Ordens

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

**Request Body:**

See OpenAPI spec for request body schema.

**Responses:**

- `201`: Criado
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X POST \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/orders' \
  -H 'Access-Token: {access-token}' \
  -H 'content-type: application/json' \
  -d '{
    "symbol": "PETR3",
    "price": 28,
    "amount": 1000,
    "side": "BUY",
    "order_type": "market",
    "origin": "order_ticket",
    "time_in_force": "day",
    "brokerage": 0,
    "status": "pending",
    "trading_account_id": 9,
    "created_at": "2021-06-19T02:59:59.999Z",
    "expires_at": "2021-06-24T02:59:59.999Z",
    "trigger_price": 28.1,
    "executed_at": null,
    "tags":
    [
      "exemplo"
    ]
  }'
```

---

### GET `/domain/portfolios/{portfolio_id}/orders/{id}`

**Status:** ❌ Not Implemented

**Summary:** Consultar ordem de um portfólio

**Description:** Obtém um objeto com os dados da ordem especificada

**Tags:** Ordens

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

- **id** (path, integer) - **Required**
  ID da ordem

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/orders/{id}' \
  -H 'Access-Token: {access-token}'
```

---

### PUT `/domain/portfolios/{portfolio_id}/orders/{id}`

**Status:** ❌ Not Implemented

**Summary:** Alterar ordem de um portfólio

**Description:** Altera os dados da ordem especificada do portfólio

**Tags:** Ordens

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

- **id** (path, integer) - **Required**
  ID da ordem

**Request Body:**

See OpenAPI spec for request body schema.

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X PUT \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/orders/{id}' \
  -H 'Access-Token: {access-token}' \
  -H 'content-type: application/json' \
  -d '{
    "price": 28,
    "amount": 1000,
    "side": "BUY",
    "time_in_force": "day",
    "trigger_price": 28.1,
    "expires_at": "2021-06-24T02:59:59.999Z",
    "executed_at": null
  }'
```

---

### DELETE `/domain/portfolios/{portfolio_id}/orders/{id}`

**Status:** ❌ Not Implemented

**Summary:** Remover ordem de um portfólio

**Description:** Cancela a ordem especificada do portfólio

**Tags:** Ordens

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

- **id** (path, integer) - **Required**
  ID da ordem

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X DELETE \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/orders/{id}' \
  -H 'Access-Token: {access-token}'
```

---

### POST `/domain/portfolios/{portfolio_id}/orders/{id}/execute`

**Status:** ❌ Not Implemented

**Summary:** Executar ordem do portfólio

**Description:** Executa a ordem especificada do portfólio, a ordem deve ser do tipo `manual` e estar com status `pending`

**Tags:** Ordens

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

- **id** (path, integer) - **Required**
  ID da ordem

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado
- `412`: Pré-condição falha
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X POST \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/orders/{id}/execute' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/domain/portfolios/{portfolio_id}/orders/pending`

**Status:** ❌ Not Implemented

**Summary:** Contar ordens pendentes de um portfólio

**Description:** Obtém a quantidade de ordens pendentes do portfólio especificado

**Tags:** Ordens

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/orders/pending' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/domain/portfolios/{portfolio_id}/orders/export`

**Status:** ❌ Not Implemented

**Summary:** Exportar ordens de um portfólio

**Description:** Executa um processo em segundo plano que gera um arquivo em formato CSV com todas as ordens contidas no portfólio especificado. Ao término do processamento, envia uma notificação via sistema com o link para download do arquivo

**Tags:** Ordens

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

**Responses:**

- `202`: Aceito para processamento em segundo plano
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado
- `429`: Requisição repetitiva

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/orders/{id}/export' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/domain/portfolios/{portfolio_id}/positions/{position_id}/orders`

**Status:** ❌ Not Implemented

**Summary:** Listar ordens de uma posição

**Description:** Obtém uma lista com as ordens da posição especificada

**Tags:** Ordens

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

- **position_id** (path, integer) - **Required**
  ID da posição

- **from** (query, string) - Optional
  Data de início da consulta

- **to** (query, string) - Optional
  Data de fim da consulta

- **page** (query, integer) - Optional
  Número da página da pesquisa

- **per** (query, integer) - Optional
  Quantidade de itens por página

- **ticker** (query, string) - Optional
  Código do ativo das ordens a serem listadas, pode ser informado um valor parcial

- **origin** (query, string) - Optional - Options: `simulator, order_ticket, robot`
  Origem das ordens a serem listadas. Aceita mais de um valor, separando por vírgula

- **status** (query, string) - Optional - Options: `pending, filled, canceled, staged, created, partially_filled, rejected, expired, replaced, done_for_day, pending_cancel, stopped, suspended, pending_new, calculated, accepted_for_bidding, pending_replace`
  Status das ordens a serem listadas. Aceita mais de um valor, separando por vírgula. Obs: Quando o valor `partially_filled` é passado, as ordens canceladas ou expiradas que anteriormente foram executadas parcialmente serão retornadas

- **order_type** (query, string) - Optional - Options: `manual, market, limit, stop_limit`
  Tipo de ordens a serem listadas. Aceita mais de um valor, separando por vírgula

- **side** (query, string) - Optional - Options: `SELL, BUY`
  Lado das ordens a serem listadas. Aceita mais de um valor, separando por vírgula

- **show_position** (query, boolean) - Optional (default: `True`)
  Determina se as ordens devem incluir as informações da posição

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/positions/{position_id}/orders?from={from}&to={to}&page={page}&per={per}&ticker={ticker}&origin={origin}&status={status}&order_type={order_type}&side={side}&show_position={show_position}' \
  -H 'Access-Token: {access-token}'
```

---

### POST `/domain/portfolios/{portfolio_id}/positions/{position_id}/orders`

**Status:** ❌ Not Implemented

**Summary:** Incluir ordem em uma posição

**Description:** Inclui uma ordem na posição especificada

**Tags:** Ordens

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

- **position_id** (path, integer) - **Required**
  ID da posição

**Request Body:**

See OpenAPI spec for request body schema.

**Responses:**

- `201`: Criado
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X POST \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/positions/{position_id}/orders' \
  -H 'Access-Token: {access-token}' \
  -H 'content-type: application/json' \
  -d '{
    "symbol": "PETR3",
    "price": 28,
    "amount": 1000,
    "side": "BUY",
    "order_type": "market",
    "origin": "order_ticket",
    "time_in_force": "day",
    "brokerage": 0,
    "status": "pending",
    "trading_account_id": 9,
    "created_at": "2021-06-19T02:59:59.999Z",
    "expires_at": "2021-06-24T02:59:59.999Z",
    "trigger_price": 28.1,
    "executed_at": null,
    "tags":
    [
      "exemplo"
    ]
  }'
```

---

### GET `/domain/portfolios/{portfolio_id}/positions/{position_id}/orders/{id}`

**Status:** ❌ Not Implemented

**Summary:** Consultar ordem de uma posição

**Description:** Obtém um objeto com os dados da ordem especificada da posição

**Tags:** Ordens

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

- **position_id** (path, integer) - **Required**
  ID da posição

- **id** (path, integer) - **Required**
  ID da ordem

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/positions/{position_id}/orders/{id}' \
  -H 'Access-Token: {access-token}'
```

---

### PUT `/domain/portfolios/{portfolio_id}/positions/{position_id}/orders/{id}`

**Status:** ❌ Not Implemented

**Summary:** Alterar ordem de uma posição

**Description:** Altera os dados da ordem especificada da posição

**Tags:** Ordens

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

- **position_id** (path, integer) - **Required**
  ID da posição

- **id** (path, integer) - **Required**
  ID da ordem

**Request Body:**

See OpenAPI spec for request body schema.

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X PUT \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/positions/{position_id}/orders/{id}' \
  -H 'Access-Token: {access-token}' \
  -H 'content-type: application/json' \
  -d '{
    "price": 28,
    "amount": 1000,
    "side": "BUY",
    "time_in_force": "day",
    "trigger_price": 28.1,
    "expires_at": "2021-06-24T02:59:59.999Z",
    "executed_at": null
  }'
```

---

### DELETE `/domain/portfolios/{portfolio_id}/positions/{position_id}/orders/{id}`

**Status:** ❌ Not Implemented

**Summary:** Remover ordem de uma posição

**Description:** Cancela a ordem especificada da posição

**Tags:** Ordens

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

- **position_id** (path, integer) - **Required**
  ID da posição

- **id** (path, integer) - **Required**
  ID da ordem

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X DELETE \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/positions/{position_id}/orders/{id}' \
  -H 'Access-Token: {access-token}'
```

---

### Outros

### GET `/domain/trading/business_days/{until}`

**Status:** ❌ Not Implemented

**Summary:** Calcular dias úteis até uma data

**Description:** Obtém um objeto com a quantidade de dias úteis até a data especificada

**Tags:** Outros

**Parameters:**

- **until** (path, string) - **Required**
  Data de referência

**Responses:**

- `200`: OK
- `400`: Requisição inválida
- `401`: Não autorizado
- `403`: Acesso negado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/trading/business_days/{until}' \
  -H 'Access-Token: {access-token}'
```

---

### Portfólios

### GET `/domain/portfolios`

**Status:** ❌ Not Implemented

**Summary:** Listar portfólios

**Description:** Obtém uma lista com todos os portfólios do usuário

**Tags:** Portfólios

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/portfolios' \
  -H 'Access-Token: {access-token}'
```

---

### POST `/domain/portfolios`

**Status:** ❌ Not Implemented

**Summary:** Incluir portfólio

**Description:** Inclui um novo portfólio vazio na conta do usuário

**Tags:** Portfólios

**Request Body:**

See OpenAPI spec for request body schema.

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado

**Example Request:**

```bash
curl -i -X POST \
  'https://api.oplab.com.br/v3/domain/portfolios' \
  -H 'Access-Token: {access-token}' \
  -H 'content-type: application/json' \
  -d '{
    "name": "Novo portfólio",
    "active": true"
  }'
```

---

### GET `/domain/portfolios/{id}`

**Status:** ❌ Not Implemented

**Summary:** Consultar portfólio

**Description:** Obtém um objeto com os dados do portfólio especificado

**Tags:** Portfólios

**Parameters:**

- **id** (path, integer) - **Required**
  ID do portfólio

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/portfolios/{id}' \
  -H 'Access-Token: {access-token}'
```

---

### PUT `/domain/portfolios/{id}`

**Status:** ❌ Not Implemented

**Summary:** Alterar portfólio

**Description:** Altera os dados do portfólio especificado

**Tags:** Portfólios

**Parameters:**

- **id** (path, integer) - **Required**
  ID do portfólio

**Request Body:**

See OpenAPI spec for request body schema.

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X PUT \
  'https://api.oplab.com.br/v3/domain/portfolios/{id}' \
  -H 'Access-Token: {access-token}' \
  -H 'content-type: application/json' \
  -d '{
    "name": "Novo portfólio",
    "active": true"
  }'
```

---

### DELETE `/domain/portfolios/{id}`

**Status:** ❌ Not Implemented

**Summary:** Remover portfólio

**Description:** Remove os dados do portfólio especificado

**Tags:** Portfólios

**Parameters:**

- **id** (path, integer) - **Required**
  ID do portfólio

**Responses:**

- `204`: Sem conteúdo
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado

**Example Request:**

```bash
curl -i -X DELETE \
  'https://api.oplab.com.br/v3/domain/portfolios/{id}' \
  -H 'Access-Token: {access-token}'
```

---

### PUT `/domain/portfolios/{id}/default`

**Status:** ❌ Not Implemented

**Summary:** Definir portfólio como padrão

**Description:** Define o portfólio especificado como padrão

**Tags:** Portfólios

**Parameters:**

- **id** (path, integer) - **Required**
  ID do portfólio

**Responses:**

- `204`: Sem conteúdo
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado

**Example Request:**

```bash
curl -i -X PUT \
  https://api.oplab.com.br/v3/domain/portfolios/{id}/default \
  -H 'Access-Token: {access-token}'
```

---

### GET `/domain/portfolios/{id}/returns`

**Status:** ❌ Not Implemented

**Summary:** Consultar retorno do portfólio

**Description:** Obtém uma lista com os dados de retorno do portfólio especificado

**Tags:** Portfólios

**Parameters:**

- **id** (path, integer) - **Required**
  ID do portfólio

- **from** (query, string) - Optional
  Data de início da consulta

- **to** (query, string) - Optional
  Data de fim da consulta

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/portfolios/{id}/returns?from={from}&to={to}' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/domain/portfolios/{id}/tags`

**Status:** ❌ Not Implemented

**Summary:** Consultar tags do portfólio

**Description:** Obtém uma lista das tags associadas ao portfólio especificado

**Tags:** Portfólios

**Parameters:**

- **id** (path, integer) - **Required**
  ID do portfólio

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/portfolios/{id}/tags' \
  -H 'Access-Token: {access-token}'
```

---

### PUT `/domain/portfolios/{id}/synchronize`

**Status:** ❌ Not Implemented

**Summary:** Ativar sincronização do portfólio

**Description:** Habilita a sincronização do portfólio especificado com uma fonte de dados

**Tags:** Portfólios

**Parameters:**

- **id** (path, integer) - **Required**
  ID do portfólio

**Request Body:**

See OpenAPI spec for request body schema.

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X PUT \
  'https://api.oplab.com.br/v3/domain/portfolios/{id}/synchronize' \
  -H 'Access-Token: {access-token}' \
  -H 'content-type: application/json' \
  -d '{
    "sync_strategy": "b3",
  }'
```

---

### DELETE `/domain/portfolios/{id}/synchronize`

**Status:** ❌ Not Implemented

**Summary:** Desativar sincronização do portfólio

**Description:** Desabilita a sincronização do portfólio especificado

**Tags:** Portfólios

**Parameters:**

- **id** (path, integer) - **Required**
  ID do portfólio

**Responses:**

- `204`: Sem conteúdo
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado

**Example Request:**

```bash
curl -i -X DELETE \
  'https://api.oplab.com.br/v3/domain/portfolios/{id}/synchronize' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/domain/portfolios/{portfolio_id}/shared_portfolios`

**Status:** ❌ Not Implemented

**Summary:** Listar compartilhamentos

**Description:** Obtém uma lista com os compartilhamentos do portfólio especificado

**Tags:** Portfólios

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

**Responses:**

- `200`: OK
- `204`: Sem conteúdo
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/{portfolio_id}/shared_portfolios' \
  -H 'Access-Token: {access-token}'
```

---

### POST `/domain/portfolios/{portfolio_id}/shared_portfolios`

**Status:** ❌ Not Implemented

**Summary:** Criar compartilhamento

**Description:** Cria um novo compartilhamento para o portfólio especificado

**Tags:** Portfólios

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

**Request Body:**

See OpenAPI spec for request body schema.

**Responses:**

- `201`: Criado
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X POST \
  'https://api.oplab.com.br/v3/domain/{portfolio_id}/shared_portfolios' \
  -H 'Access-Token: {access-token}' \
  -H 'content-type: application/json' \
  -d '{
    "advisor_id": 2,
    "access_level": "read"
  }'
```

---

### GET `/domain/portfolios/{portfolio_id}/shared_portfolios/{id}`

**Status:** ❌ Not Implemented

**Summary:** Consultar um compartilhamento

**Description:** Obtém um objeto com os dados do compartilhamento de portfólio especificado

**Tags:** Portfólios

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

- **id** (path, integer) - **Required**
  ID do compartilhamento de portfólio

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/{portfolio_id}/shared_portfolios/{id}' \
  -H 'Access-Token: {access-token}'
```

---

### PUT `/domain/portfolios/{portfolio_id}/shared_portfolios/{id}`

**Status:** ❌ Not Implemented

**Summary:** Alterar compartilhamento

**Description:** Altera o nível de acesso do compartilhamento de portfólio especificado

**Tags:** Portfólios

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

- **id** (path, integer) - **Required**
  ID do compartilhamento de portfólio

**Request Body:**

See OpenAPI spec for request body schema.

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X PUT \
  'https://api.oplab.com.br/v3/domain/{portfolio_id}/shared_portfolios/{id}' \
  -H 'Access-Token: {access-token}' \
  -H 'content-type: application/json' \
  -d '{
    "access_level": "write"
  }'
```

---

### DELETE `/domain/portfolios/{portfolio_id}/shared_portfolios/{id}`

**Status:** ❌ Not Implemented

**Summary:** Desativar compartilhamento

**Description:** Desativa o compartilhamento de portfólio especificado

**Tags:** Portfólios

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

- **id** (path, integer) - **Required**
  ID do compartilhamento de portfólio

**Responses:**

- `204`: Sem conteúdo
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X DELETE \
  'https://api.oplab.com.br/v3/domain/{portfolio_id}/shared_portfolios/{id}' \
  -H 'Access-Token: {access-token}'
```

---

### Posições

### GET `/domain/portfolios/{portfolio_id}/positions`

**Status:** ❌ Not Implemented

**Summary:** Listar posições

**Description:** Obtém uma lista com as posições do portfólio especificado

**Tags:** Posições

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

- **status** (query, string) - Optional (default: `open`) - Options: `open, closed, all`
  Status das posições a serem listadas

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/positions?status={status}' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/domain/portfolios/{portfolio_id}/positions/{id}`

**Status:** ❌ Not Implemented

**Summary:** Consultar uma posição

**Description:** Obtém um objeto com os dados da posição especificada

**Tags:** Posições

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

- **id** (path, integer) - **Required**
  ID da posição

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/positions/{id}' \
  -H 'Access-Token: {access-token}'
```

---

### PUT `/domain/portfolios/{portfolio_id}/positions/{id}`

**Status:** ❌ Not Implemented

**Summary:** Alterar uma posição

**Description:** Altera os dados da posição especificada, podendo move-la para outra estratégia (nova ou existente)

**Tags:** Posições

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

- **id** (path, integer) - **Required**
  ID da posição

**Request Body:**

See OpenAPI spec for request body schema.

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X PUT \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/positions/{id}' \
  -H 'Access-Token: {access-token}' \
  -H 'content-type: application/json' \
  -d '{
    "name": "Exemplo",
    "positive_scenario_probability": 10,
    "strategy_id": 1,
    "strategy_name": "Estratégia nova",
    "orders":
    [
      100,
      101
    ]
  }'
```

---

### DELETE `/domain/portfolios/{portfolio_id}/positions/{id}`

**Status:** ❌ Not Implemented

**Summary:** Remover uma posição

**Description:** Remove os dados da posição especificada

**Tags:** Posições

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

- **id** (path, integer) - **Required**
  ID da posição

**Responses:**

- `204`: Sem conteúdo
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X DELETE \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/positions/{id}' \
  -H 'Access-Token: {access-token}'
```

---

### PUT `/domain/portfolios/{portfolio_id}/positions/{id}/tag/{tag}`

**Status:** ❌ Not Implemented

**Summary:** Incluir tag em uma posição

**Description:** Inclui uma determinada tag na posição especificada

**Tags:** Posições

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

- **id** (path, integer) - **Required**
  ID da posição

- **tag** (path, string) - **Required**
  Tag a ser incluida

**Responses:**

- `204`: Sem conteúdo
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado

**Example Request:**

```bash
curl -i -X PUT \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/positions/{id}/tag/{tag}' \
  -H 'Access-Token: {access-token}'
```

---

### PUT `/domain/portfolios/{portfolio_id}/positions/{id}/untag/{tag}`

**Status:** ❌ Not Implemented

**Summary:** Remover tag de uma posição

**Description:** Remove uma determinada tag da posição especificada

**Tags:** Posições

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

- **id** (path, integer) - **Required**
  ID da posição

- **tag** (path, string) - **Required**
  Tag a ser removida

**Responses:**

- `204`: Sem conteúdo
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado

**Example Request:**

```bash
curl -i -X PUT \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/positions/{id}/untag/{tag}' \
  -H 'Access-Token: {access-token}'
```

---

### PUT `/domain/portfolios/{portfolio_id}/positions/{id}/commit`

**Status:** ❌ Not Implemented

**Summary:** Consolidar uma posição

**Description:** Consolida uma posição simulada especificada

**Tags:** Posições

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

- **id** (path, integer) - **Required**
  ID da posição

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X PUT \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/positions/{id}/commit' \
  -H 'Access-Token: {access-token}'
```

---

### PUT `/domain/portfolios/{portfolio_id}/positions/{id}/close`

**Status:** ❌ Not Implemented

**Summary:** Fechar uma posição

**Description:** Altera o status da posição especificada para fechada enviando uma contra-ordem

**Tags:** Posições

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

- **id** (path, integer) - **Required**
  ID da posição

**Request Body:**

See OpenAPI spec for request body schema.

**Responses:**

- `200`: OK
- `204`: Sem conteúdo
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X PUT \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/positions/{id}/close' \
  -H 'Access-Token: {access-token}' \
  -H 'content-type: application/json' \
  -d '{
    "exercise": true
  }'
```

---

### Robôs

### GET `/domain/portfolios/{portfolio_id}/robots`

**Status:** ❌ Not Implemented

**Summary:** Listar robôs

**Description:** Obtém uma lista com os dados de todos os robôs do usuário

**Tags:** Robôs

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

- **from** (query, string) - Optional
  Data de início da consulta

- **to** (query, string) - Optional
  Data de fim da consulta

- **page** (query, integer) - Optional
  Número da página da pesquisa

- **per** (query, integer) - Optional
  Quantidade de itens por página

- **status** (query, integer) - Optional - Options: `0, 1, 2, 3, 4, 5, 6, 7, 8, 11, 12, 13, 14`
  Status dos robôs a serem listados. Aceita mais de um valor, sendo apenas números separados por vírgula

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/robots?from={from}&to={to}&page={page}&per={per}&status={status}' \
  -H 'Access-Token: {access-token}'
```

---

### POST `/domain/portfolios/{portfolio_id}/robots`

**Status:** ❌ Not Implemented

**Summary:** Incluir robô

**Description:** Inclui um robô no portfólio especificado

**Tags:** Robôs

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

**Request Body:**

See OpenAPI spec for request body schema.

**Responses:**

- `200`: OK
- `400`: Requisição inválida
- `401`: Não autorizado
- `403`: Acesso negado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X POST \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/robots' \
  -H 'Access-Token: {access-token}' \
  -H 'content-type: application/json' \
  -d '{
    "trading_account_id": 9,
    "spread": -40,
    "strategy": {
      "id": null,
      "name": "Trava de alta",
      "underlying": "PETR4"
    },
    "legs":
    [
      {
        "symbol": "PETRI216",
        "target_amount": 1000,
        "side": "SELL",
        "depth": 1
      },
      {
        "symbol": "PETRI258",
        "target_amount": 1000,
        "side": "BUY",
        "depth": 1
      }
    ],
    "debug": 4,
    "mode": "secure",
    "expire_date": "2021-08-27",
    "start_time": "11:00",
    "stop_time": "16:00"
  }'
```

---

### GET `/domain/portfolios/{portfolio_id}/robots/{id}`

**Status:** ❌ Not Implemented

**Summary:** Consultar robô

**Description:** Obtém um objeto com os dados do robô especificado

**Tags:** Robôs

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

- **id** (path, integer) - **Required**
  ID do robô

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/robots/{id}'\
  -H 'Access-Token: {access-token}'
```

---

### PUT `/domain/portfolios/{portfolio_id}/robots/{id}`

**Status:** ❌ Not Implemented

**Summary:** Alterar robô

**Description:** Envia um comando de alteração para o robô. Só é possível alterar robôs que estão em execução, pausados ou esperando horário de execução

**Tags:** Robôs

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

- **id** (path, integer) - **Required**
  ID do robô

**Request Body:**

See OpenAPI spec for request body schema.

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X PUT \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/robots/{id}' \
  -H 'Access-Token: {access-token}' \
  -H 'content-type: application/json' \
  -d '{
    "spread": 200,
    "expire_date": "2021-08-21",
    "start_time": "10:00",
    "stop_time": "15:00"
  }'
```

---

### DELETE `/domain/portfolios/{portfolio_id}/robots/{id}`

**Status:** ❌ Not Implemented

**Summary:** Cancelar robô

**Description:** Envia um comando de cancelamento para o robô. Só é possível cancelar robôs que estão em execução, pausados ou esperando horário de execução

**Tags:** Robôs

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

- **id** (path, integer) - **Required**
  ID do robô

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X DELETE \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/robots/{id}' \
  -H 'Access-Token: {access-token}'
```

---

### POST `/domain/portfolios/{portfolio_id}/robots/{id}/pause`

**Status:** ❌ Not Implemented

**Summary:** Pausar robô

**Description:** Envia um comando de pausa para o robô. Só é possível pausar robôs que estão em execução ou esperando horário de execução

**Tags:** Robôs

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

- **id** (path, integer) - **Required**
  ID do robô

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X POST \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/robots/{id}/pause' \
  -H 'Access-Token: {access-token}'
```

---

### POST `/domain/portfolios/{portfolio_id}/robots/{id}/resume`

**Status:** ❌ Not Implemented

**Summary:** Retomar robô

**Description:** Envia um comando de retorno à execução para o robô. Só é possível retomar a execução de robôs que estão em pausa

**Tags:** Robôs

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

- **id** (path, integer) - **Required**
  ID do robô

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X POST \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/robots/{id}/resume' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/domain/portfolios/{portfolio_id}/robots/{id}/log`

**Status:** ❌ Not Implemented

**Summary:** Consultar logs do robô

**Description:** Obtém um arquivo com os logs do robô especificado

**Tags:** Robôs

**Parameters:**

- **portfolio_id** (path, integer) - **Required**
  ID do portfólio

- **id** (path, integer) - **Required**
  ID do robô

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/portfolios/{portfolio_id}/robots/{id}/log' \
  -H 'Access-Token: {access-token}'
```

---

### Usuário

### POST `/domain/password_reset`

**Status:** ❌ Not Implemented

**Summary:** Recuperar senha

**Description:** Envia link de recuperação de senha para o e-mail do usuário

**Tags:** Usuário

**Request Body:**

See OpenAPI spec for request body schema.

**Responses:**

- `204`: Sem conteúdo
- `400`: Requisição inválida

**Example Request:**

```bash
curl -i -X POST \
  'https://api.oplab.com.br/v3/domain/password' \
  -H 'Access-Token: {access-token}' \
  -H 'content-type: application/json' \
  -d '{
    "email": "joao.da.silva@oplab.com.br"
  }'
```

---

### POST `/domain/users/authenticate`

**Status:** ❌ Not Implemented

**Summary:** Autenticação

**Description:** Autentica o usuário no sistema a partir do email e senha

**Tags:** Usuário

**Parameters:**

- **for** (query, string) - Optional (default: `default`) - Options: `default, chart`
  Contexto de autenticação

**Request Body:**

See OpenAPI spec for request body schema.

**Responses:**

- `200`: OK
- `400`: Requisição inválida
- `401`: Não autorizado
- `403`: Acesso negado

**Example Request:**

```bash
curl -i -X POST \
  'https://api.oplab.com.br/v3/domain/users/authenticate' \
  -H 'content-type: application/json' \
  -d '{
    "email": "joao.da.silva@oplab.com.br",
    "password": "exemplo123"
  }'
```

---

### GET `/domain/users/authorize`

**Status:** ❌ Not Implemented

**Summary:** Autorização

**Description:** Autoriza o acesso ao sistema a partir do token de acesso

**Tags:** Usuário

**Parameters:**

- **for** (query, string) - Optional (default: `default`) - Options: `default, chart`
  Contexto de autenticação

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `402`: Pagamento Requerido

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/users/authorize' \
  -H 'Access-Token: {access-token}'
```

---

### GET `/domain/users/settings`

**Status:** ❌ Not Implemented

**Summary:** Listar configurações

**Description:** Obtém a lista de configurações do usuário

**Tags:** Usuário

**Parameters:**

- **group** (query, string) - Optional - Options: `admin, producer`
  Grupo das configurações a serem filtradas na consulta. Aceita mais de um valor, separando por vírgula

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/users/settings' \
  -H 'Access-Token: {access-token}'
```

---

### POST `/domain/users/settings`

**Status:** ❌ Not Implemented

**Summary:** Atualizar configurações

**Description:** Atualiza as configurações gerais da conta do usuário, com exceção de permissões administrativas

**Tags:** Usuário

**Request Body:**

See OpenAPI spec for request body schema.

**Responses:**

- `204`: Sem conteúdo
- `400`: Requisição inválida
- `401`: Não autorizado
- `402`: Pagamento Requerido
- `403`: Acesso negado

**Example Request:**

```bash
curl -i -X POST \
'https://api.oplab.com.br/v3/domain/users/settings' \
  -H 'Access-Token: {access-token}' \
  -H 'content-type: application/json' \
  -d '{
    "preferences": "{\"interest_rate_type\": \"SELIC\", \"interest_rate_value\": 2.649873258040536, \"broker\": \"OTHER\", \"brokerage_fee\": 0.8, \"order_amount\": 1000, \"simulate_price_strategy\": \"LAST\", \"position_price_strategy\": [\"BOOK\",\"LAST\",\"THEORETICAL\"], \"simulate_with_brokerage_and_fees\": true, \"custom_perspective\": [\"bid\",\"ask\"], \"default_web_app_version\": null, \"tinted_moneyness\": 10, \"side_watchlist\": true, \"robot_limit\": 10, \"close_positions_automatically\": false}"
  }'
```

---

### GET `/domain/users/settings/producer`

**Status:** ❌ Not Implemented

**Summary:** Alterar configurações de publicação

**Description:** Altera e retorna as configurações de publicação do usuário

**Tags:** Usuário

**Request Body:**

See OpenAPI spec for request body schema.

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `412`: Falha na pré-condição
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X PUT \
  'https://api.oplab.com.br/v3/domain/users/settings/producer' \
  -H 'Access-Token: {access-token}' \
  -H 'content-type: application/json' \
  -d '{
    "logo": "data:<mediatype>;base64,<data>",
    "color": "#FFFFFF",
    "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin porttitor ut nulla nec blandit. Vivamus eu enim et elit imperdiet ullamcorper nec id justo. Sed et vestibulum lorem, ut euismod ante. Sed eu elementum augue, eu egestas lectus. Nam enim quam, viverra eu quam et, lacinia vulputate sem. Pellentesque lacinia gravida placerat. Nullam erat purus, mattis non dui vel, ultricies malesuada arcu. Ut dictum neque eget nulla volutpat, ac maximus purus malesuada. Proin quis ligula semper, tincidunt odio et, aliquet nulla."
  }'
```

---

### PUT `/domain/users/{id}`

**Status:** ❌ Not Implemented

**Summary:** Alterar usuário

**Description:** Altera os dados do usuário

**Tags:** Usuário

**Parameters:**

- **id** (path, integer) - **Required**
  ID do usuário

**Request Body:**

See OpenAPI spec for request body schema.

**Responses:**

- `204`: Sem conteúdo
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X PUT \
  'https://api.oplab.com.br/v3/domain/users/{id}' \
  -H 'Access-Token: {access-token}' \
  -H 'content-type: application/json' \
  -d '{
    "name": "João",
    "document_type": "CPF",
    "document_number": "12345678900",
    "phone_area_code": "11",
    "phone_number": "12345678"
  }'
```

---

### GET `/domain/users/advisors`

**Status:** ❌ Not Implemented

**Summary:** Listar usuários do tipo consultor

**Description:** Lista todos os usuários do tipo consultor de investimentos

**Tags:** Usuário

**Responses:**

- `200`: OK
- `204`: Sem conteúdo
- `401`: Não autorizado
- `403`: Acesso negado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/users/advisors' \
  -H 'Access-Token: {access-token}'
```

---

### Watchlists

### GET `/domain/watchlists`

**Status:** ❌ Not Implemented

**Summary:** Listar watchlists

**Description:** Obtém uma lista com todas as watchlists do usuário

**Tags:** Watchlists

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/watchlists' \
  -H 'Access-Token: {access-token}'
```

---

### POST `/domain/watchlists`

**Status:** ❌ Not Implemented

**Summary:** Incluir watchlist

**Description:** Inclui uma nova watchlist para o usuário

**Tags:** Watchlists

**Request Body:**

See OpenAPI spec for request body schema.

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X POST \
  'https://api.oplab.com.br/v3/domain/watchlists' \
  -H 'Access-Token: {access-token}' \
  -H 'content-type: application/json' \
  -d '{
    "name": "Minha super watchlist",
    "is_default": false,
    "sort": 1
  }'
```

---

### GET `/domain/watchlists/{id}`

**Status:** ❌ Not Implemented

**Summary:** Consultar watchlist

**Description:** Obtém os dados da watchlist especificada

**Tags:** Watchlists

**Parameters:**

- **id** (path, integer) - **Required**
  ID da watchlist. Enviando a palavra `default`, será obtida a watchlist padrão

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado

**Example Request:**

```bash
curl -i -X GET \
  'https://api.oplab.com.br/v3/domain/watchlists/{id}' \
  -H 'Access-Token: {access-token}'
```

---

### PUT `/domain/watchlists/{id}`

**Status:** ❌ Not Implemented

**Summary:** Alterar watchlist

**Description:** Altera os dados da watchlist determinada

**Tags:** Watchlists

**Parameters:**

- **id** (path, integer) - **Required**
  ID da watchlist. Enviando a palavra `default`, será alterada a watchlist padrão

**Request Body:**

See OpenAPI spec for request body schema.

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X PUT \
  'https://api.oplab.com.br/v3/domain/watchlists/{id}' \
  -H 'Access-Token: {access-token}' \
  -H 'content-type: application/json' \
  -d '{
    "name": "Minha watchlist favorita",
    "is_default": true,
    "sort": 1
  }'
```

---

### DELETE `/domain/watchlists/{id}`

**Status:** ❌ Not Implemented

**Summary:** Remover watchlist

**Description:** Remove uma determinada watchlist

**Tags:** Watchlists

**Parameters:**

- **id** (path, integer) - **Required**
  ID da watchlist. Enviando a palavra `default`, será removida a watchlist padrão

**Responses:**

- `204`: Sem conteúdo
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado
- `422`: Entidade não processada

**Example Request:**

```bash
curl -i -X DELETE \
  'https://api.oplab.com.br/v3/domain/watchlists/{id}' \
  -H 'Access-Token: {access-token}'
```

---

### POST `/domain/watchlists/{id}/{symbol}`

**Status:** ❌ Not Implemented

**Summary:** Incluir instrumento na watchlist

**Description:** Inclui um determinado instrumento na watchlist determinada

**Tags:** Watchlists

**Parameters:**

- **id** (path, integer) - **Required**
  ID da watchlist. Enviando a palavra `default`, será incluido na watchlist padrão

- **symbol** (path, string) - **Required**
  Código de negociação do instrumento

**Request Body:**

See OpenAPI spec for request body schema.

**Responses:**

- `200`: OK
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado

**Example Request:**

```bash
curl -i -X POST \
  'https://api.oplab.com.br/v3/domain/watchlists/{id}/{symbol}' \
  -H 'Access-Token: {access-token}' \
  -H 'content-type: application/json' \
  -d '{
    "weight": 10
  }'
```

---

### DELETE `/domain/watchlists/{id}/{symbol}`

**Status:** ❌ Not Implemented

**Summary:** Remover instrumento da watchlist

**Description:** Remove um determinado instrumento da watchlist determinada

**Tags:** Watchlists

**Parameters:**

- **id** (path, integer) - **Required**
  ID da watchlist. Enviando a palavra `default`, será removido da watchlist padrão

- **symbol** (path, string) - **Required**
  Código de negociação do instrumento

**Responses:**

- `204`: Sem conteúdo
- `401`: Não autorizado
- `403`: Acesso negado
- `404`: Não encontrado

**Example Request:**

```bash
curl -i -X DELETE \
  'https://api.oplab.com.br/v3/domain/watchlists/{id}/{symbol}' \
  -H 'Access-Token: {access-token}'
```

---


## Summary Table

| Method | Path | Summary | Status |
|--------|------|---------|--------|
| GET | `/domain/brokers` | Listar corretoras | ❌ Not Implemented |
| GET | `/domain/brokers/{id}` | Consultar corretora | ❌ Not Implemented |
| POST | `/domain/brokers/{id}/sign_up` | Cadastrar usuário na corretora | ❌ Not Implemented |
| GET | `/domain/notifications` | Listar notificações | ❌ Not Implemented |
| POST | `/domain/notifications/delete_all` | Remover notificações | ❌ Not Implemented |
| GET | `/domain/notifications/preferences` | Consultar preferências | ❌ Not Implemented |
| POST | `/domain/notifications/preferences` | Alterar preferências | ❌ Not Implemented |
| POST | `/domain/notifications/read_all` | Marcar notificações como lidas | ❌ Not Implemented |
| GET | `/domain/notifications/unread` | Contar notificações não lidas | ❌ Not Implemented |
| DELETE | `/domain/notifications/{id}` | Remover notificação | ❌ Not Implemented |
| GET | `/domain/notifications/{id}` | Consultar notificação | ❌ Not Implemented |
| PUT | `/domain/notifications/{id}` | Alterar notificação | ❌ Not Implemented |
| POST | `/domain/password_reset` | Recuperar senha | ❌ Not Implemented |
| GET | `/domain/portfolios` | Listar portfólios | ❌ Not Implemented |
| POST | `/domain/portfolios` | Incluir portfólio | ❌ Not Implemented |
| DELETE | `/domain/portfolios/{id}` | Remover portfólio | ❌ Not Implemented |
| GET | `/domain/portfolios/{id}` | Consultar portfólio | ❌ Not Implemented |
| PUT | `/domain/portfolios/{id}` | Alterar portfólio | ❌ Not Implemented |
| PUT | `/domain/portfolios/{id}/default` | Definir portfólio como padrão | ❌ Not Implemented |
| GET | `/domain/portfolios/{id}/returns` | Consultar retorno do portfólio | ❌ Not Implemented |
| DELETE | `/domain/portfolios/{id}/synchronize` | Desativar sincronização do portfólio | ❌ Not Implemented |
| PUT | `/domain/portfolios/{id}/synchronize` | Ativar sincronização do portfólio | ❌ Not Implemented |
| GET | `/domain/portfolios/{id}/tags` | Consultar tags do portfólio | ❌ Not Implemented |
| GET | `/domain/portfolios/{portfolio_id}/orders` | Listar ordens de um portfólio | ❌ Not Implemented |
| POST | `/domain/portfolios/{portfolio_id}/orders` | Incluir ordem em um portfólio | ❌ Not Implemented |
| GET | `/domain/portfolios/{portfolio_id}/orders/export` | Exportar ordens de um portfólio | ❌ Not Implemented |
| GET | `/domain/portfolios/{portfolio_id}/orders/pending` | Contar ordens pendentes de um portfólio | ❌ Not Implemented |
| DELETE | `/domain/portfolios/{portfolio_id}/orders/{id}` | Remover ordem de um portfólio | ❌ Not Implemented |
| GET | `/domain/portfolios/{portfolio_id}/orders/{id}` | Consultar ordem de um portfólio | ❌ Not Implemented |
| PUT | `/domain/portfolios/{portfolio_id}/orders/{id}` | Alterar ordem de um portfólio | ❌ Not Implemented |
| POST | `/domain/portfolios/{portfolio_id}/orders/{id}/execute` | Executar ordem do portfólio | ❌ Not Implemented |
| GET | `/domain/portfolios/{portfolio_id}/positions` | Listar posições | ❌ Not Implemented |
| DELETE | `/domain/portfolios/{portfolio_id}/positions/{id}` | Remover uma posição | ❌ Not Implemented |
| GET | `/domain/portfolios/{portfolio_id}/positions/{id}` | Consultar uma posição | ❌ Not Implemented |
| PUT | `/domain/portfolios/{portfolio_id}/positions/{id}` | Alterar uma posição | ❌ Not Implemented |
| PUT | `/domain/portfolios/{portfolio_id}/positions/{id}/close` | Fechar uma posição | ❌ Not Implemented |
| PUT | `/domain/portfolios/{portfolio_id}/positions/{id}/commit` | Consolidar uma posição | ❌ Not Implemented |
| PUT | `/domain/portfolios/{portfolio_id}/positions/{id}/tag/{tag}` | Incluir tag em uma posição | ❌ Not Implemented |
| PUT | `/domain/portfolios/{portfolio_id}/positions/{id}/untag/{tag}` | Remover tag de uma posição | ❌ Not Implemented |
| GET | `/domain/portfolios/{portfolio_id}/positions/{position_id}/orders` | Listar ordens de uma posição | ❌ Not Implemented |
| POST | `/domain/portfolios/{portfolio_id}/positions/{position_id}/orders` | Incluir ordem em uma posição | ❌ Not Implemented |
| DELETE | `/domain/portfolios/{portfolio_id}/positions/{position_id}/orders/{id}` | Remover ordem de uma posição | ❌ Not Implemented |
| GET | `/domain/portfolios/{portfolio_id}/positions/{position_id}/orders/{id}` | Consultar ordem de uma posição | ❌ Not Implemented |
| PUT | `/domain/portfolios/{portfolio_id}/positions/{position_id}/orders/{id}` | Alterar ordem de uma posição | ❌ Not Implemented |
| GET | `/domain/portfolios/{portfolio_id}/robots` | Listar robôs | ❌ Not Implemented |
| POST | `/domain/portfolios/{portfolio_id}/robots` | Incluir robô | ❌ Not Implemented |
| DELETE | `/domain/portfolios/{portfolio_id}/robots/{id}` | Cancelar robô | ❌ Not Implemented |
| GET | `/domain/portfolios/{portfolio_id}/robots/{id}` | Consultar robô | ❌ Not Implemented |
| PUT | `/domain/portfolios/{portfolio_id}/robots/{id}` | Alterar robô | ❌ Not Implemented |
| GET | `/domain/portfolios/{portfolio_id}/robots/{id}/log` | Consultar logs do robô | ❌ Not Implemented |
| POST | `/domain/portfolios/{portfolio_id}/robots/{id}/pause` | Pausar robô | ❌ Not Implemented |
| POST | `/domain/portfolios/{portfolio_id}/robots/{id}/resume` | Retomar robô | ❌ Not Implemented |
| GET | `/domain/portfolios/{portfolio_id}/shared_portfolios` | Listar compartilhamentos | ❌ Not Implemented |
| POST | `/domain/portfolios/{portfolio_id}/shared_portfolios` | Criar compartilhamento | ❌ Not Implemented |
| DELETE | `/domain/portfolios/{portfolio_id}/shared_portfolios/{id}` | Desativar compartilhamento | ❌ Not Implemented |
| GET | `/domain/portfolios/{portfolio_id}/shared_portfolios/{id}` | Consultar um compartilhamento | ❌ Not Implemented |
| PUT | `/domain/portfolios/{portfolio_id}/shared_portfolios/{id}` | Alterar compartilhamento | ❌ Not Implemented |
| GET | `/domain/portfolios/{portfolio_id}/strategies` | Listar estratégias | ❌ Not Implemented |
| POST | `/domain/portfolios/{portfolio_id}/strategies` | Incluir estratégia | ❌ Not Implemented |
| DELETE | `/domain/portfolios/{portfolio_id}/strategies/{id}` | Remover estratégia | ❌ Not Implemented |
| GET | `/domain/portfolios/{portfolio_id}/strategies/{id}` | Consultar estratégia | ❌ Not Implemented |
| PUT | `/domain/portfolios/{portfolio_id}/strategies/{id}/close` | Fechar estratégia | ❌ Not Implemented |
| PUT | `/domain/portfolios/{portfolio_id}/strategies/{id}/commit` | Consolidar estratégia | ❌ Not Implemented |
| PUT | `/domain/portfolios/{portfolio_id}/strategies/{id}/rename` | Renomear estratégia | ❌ Not Implemented |
| GET | `/domain/trading/business_days/{until}` | Calcular dias úteis até uma data | ❌ Not Implemented |
| GET | `/domain/trading_accounts` | Listar contas de trade | ❌ Not Implemented |
| GET | `/domain/trading_accounts/{id}` | Consultar conta de trade | ❌ Not Implemented |
| PUT | `/domain/trading_accounts/{id}/cancel` | Cancelar conta de trade | ❌ Not Implemented |
| GET | `/domain/trading_accounts/{id}/pending_terms` | Listar termos pendentes da conta de trade | ❌ Not Implemented |
| POST | `/domain/trading_accounts/{trading_account_id}/agree/{term_id}` | Aceitar termo da corretora | ❌ Not Implemented |
| GET | `/domain/trading_accounts/{trading_account_id}/events` | Listar eventos da conta de trade | ❌ Not Implemented |
| GET | `/domain/trading_accounts/{trading_account_id}/events/{id}` | Consultar evento da conta de trade | ❌ Not Implemented |
| GET | `/domain/users/advisors` | Listar usuários do tipo consultor | ❌ Not Implemented |
| POST | `/domain/users/authenticate` | Autenticação | ❌ Not Implemented |
| GET | `/domain/users/authorize` | Autorização | ❌ Not Implemented |
| GET | `/domain/users/settings` | Listar configurações | ❌ Not Implemented |
| POST | `/domain/users/settings` | Atualizar configurações | ❌ Not Implemented |
| GET | `/domain/users/settings/producer` | Alterar configurações de publicação | ❌ Not Implemented |
| PUT | `/domain/users/{id}` | Alterar usuário | ❌ Not Implemented |
| GET | `/domain/watchlists` | Listar watchlists | ❌ Not Implemented |
| POST | `/domain/watchlists` | Incluir watchlist | ❌ Not Implemented |
| DELETE | `/domain/watchlists/{id}` | Remover watchlist | ❌ Not Implemented |
| GET | `/domain/watchlists/{id}` | Consultar watchlist | ❌ Not Implemented |
| PUT | `/domain/watchlists/{id}` | Alterar watchlist | ❌ Not Implemented |
| DELETE | `/domain/watchlists/{id}/{symbol}` | Remover instrumento da watchlist | ❌ Not Implemented |
| POST | `/domain/watchlists/{id}/{symbol}` | Incluir instrumento na watchlist | ❌ Not Implemented |
| GET | `/market/companies` | Consultar uma lista de companhias | ❌ Not Implemented |
| GET | `/market/exchanges` | Listar de bolsas de valores | ❌ Not Implemented |
| GET | `/market/exchanges/{uid}` | Consultar bolsa de valores | ❌ Not Implemented |
| GET | `/market/historical/instruments` | Consultar dados dos instrumentos em determinada data | ❌ Not Implemented |
| GET | `/market/historical/options/{spot}/{from}/{to}` | Consultar histórico das opções de um ativo | ❌ Not Implemented |
| GET | `/market/historical/{symbol}/{resolution}` | Consultar dados históricos de um instrumento | ❌ Not Implemented |
| GET | `/market/instruments` | Consultar detalhes de uma lista de instrumentos | ❌ Not Implemented |
| GET | `/market/instruments/search` | Listar instrumentos | ❌ Not Implemented |
| GET | `/market/instruments/series/{symbol}` | Listar séries de opções de um instrumento | ❌ Not Implemented |
| GET | `/market/instruments/{symbol}` | Consultar um instrumento | ❌ Not Implemented |
| GET | `/market/interest_rates` | Listar taxas de juros | ❌ Not Implemented |
| GET | `/market/interest_rates/{id}` | Consultar taxa de juros | ✅ Implemented |
| GET | `/market/options/bs` | Consultar Black-Scholes de uma opção | ❌ Not Implemented |
| GET | `/market/options/details/{symbol}` | Consultar uma opção | ❌ Not Implemented |
| GET | `/market/options/powders` | Listar principais pozinhos | ❌ Not Implemented |
| GET | `/market/options/strategies/covered` | Listar opções para estratégias cobertas | ❌ Not Implemented |
| GET | `/market/options/{symbol}` | Listar opções de um ativo | ✅ Implemented |
| GET | `/market/quote` | Consultar cotações de uma lista de instrumentos | ❌ Not Implemented |
| GET | `/market/statistics/ranking/correl_ibov` | Listar opções ordenadas pela correlação com IBOV | ❌ Not Implemented |
| GET | `/market/statistics/ranking/m9_m21` | Listar opções com as maiores tendências de alta/baixa | ❌ Not Implemented |
| GET | `/market/statistics/ranking/oplab_score` | Listar ações ordenadas pelo OpLab score | ❌ Not Implemented |
| GET | `/market/statistics/ranking/{attribute}` | Listar companhias ordenadas por um atributo fundamentalista | ❌ Not Implemented |
| GET | `/market/statistics/realtime/best_covered_options_rates/{type}` | Listar opções com as maiores taxas de lucro | ❌ Not Implemented |
| GET | `/market/statistics/realtime/highest_options_variation/{type}` | Listar opções com as maiores variações | ❌ Not Implemented |
| GET | `/market/statistics/realtime/highest_options_volume` | Listar maiores volumes em opções | ❌ Not Implemented |
| GET | `/market/status` | Consultar status do mercado | ❌ Not Implemented |
| GET | `/market/stocks` | Listar ações que possuem opções | ❌ Not Implemented |
| GET | `/market/stocks/all` | Listar todas as ações | ❌ Not Implemented |
| GET | `/market/stocks/{symbol}` | Consultar uma ação | ✅ Implemented |
