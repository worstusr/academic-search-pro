# 🔍 Academic Search Pro - Buscador Acadêmico Inteligente

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28.0-orange)

## 🌟 Visão Geral
O Academic Search Pro é uma ferramenta avançada de busca acadêmica que utiliza a API do Google Search com:
- Filtros inteligentes para conteúdo acadêmico
- Sistema de cache otimizado
- Visualização de dados integrada
- Interface amigável com Streamlit

## 🛠️ Funcionalidades Principais

### 🔎 Busca Aprimorada
- **Auto-completação** de operadores acadêmicos (`intitle:"paper"`, `site:.edu`, etc.)
- **Três modos de busca**:
  - Por tipo de arquivo (PDF, DOCX, etc.)
  - Em sites específicos (ex: `mit.edu`)
  - Busca personalizada
- **Filtros avançados**:
  - Por idioma
  - Por ano mínimo de publicação

### 🧠 Processamento Inteligente
- Classificação automática em **Academic** ou **General**
- Filtro de domínios não acadêmicos
- Validação de links (remove executáveis, arquivos compactados, etc.)

### ⚡ Sistema de Cache
- Armazenamento local em JSON
- Validade de 24 horas
- Indexação por hash MD5 da query

### 📊 Visualização de Dados
- Nuvem de palavras dos resultados
- Gráfico de distribuição por domínio
- Paginação inteligente

## 🚀 Como Executar

### Pré-requisitos
- Python 3.8+
- Dependências listadas no `requirements.txt`

### Instalação
```bash
git clone [seu-repositorio]
cd academic-search-pro
pip install -r requirements.txt
```

### Execução
```bash
streamlit run app.py
```
- A aplicação estará disponível em http://localhost:8501

# 🧩 Estrutura do Código

## Módulos Principais

### 1 - Configuração
- User Agents rotativos
- Sistema de cache
### 2 - Processamento
- is_valid_link() - Filtra links indesejados
- get_domain_type() - Classifica domínios
- enhance_query() - Aprimora a query de busca
### 3 - Interface
- Formulário de busca interativo
- Exibição paginada de resultados
- Visualizações gráficas

# Fluxo Principal

![](/docs/diagrama_fluxo.svg)

# 📌 Exemplo de Uso
## 1. Selecione o tipo de busca:
- Arquivo: Para artigos em PDF/DOCX
- Site Específico: Para universidades/revistas
- Personalizada: Busca livre
## 2. Aplique filtros acadêmicos:
```bash
"machine learning" → "machine learning intitle:'paper' OR site:.edu"
```
## 3. Explore os resultados com:
- Filtros por tipo (Acadêmico/Geral)
- Paginação
- Visualizações gráficas
---
### Contribuições são bem-vindas! 
#### Desenvolvido com ❤️ Mogwai Estevan
