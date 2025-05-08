import streamlit as st
from googlesearch import search as google_search
from urllib.parse import urlparse
from collections import Counter
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import random
import time
import hashlib
import os
import json
from typing import List, Dict, Optional

# --- Configuração de User Agents ---
USER_AGENTS: List[str] = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
]

# --- Sistema de Cache ---
CACHE_DIR: str = "search_cache"
os.makedirs(CACHE_DIR, exist_ok=True)


def get_cache_filename(search_query: str) -> str:
    """Gera um nome de arquivo baseado no hash da query"""
    return os.path.join(CACHE_DIR, hashlib.md5(search_query.encode()).hexdigest() + ".json")


def get_cached_results(search_query: str) -> Optional[List[Dict[str, str]]]:
    """Recupera resultados do cache se existirem e forem recentes"""
    cache_file = get_cache_filename(search_query)
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding='utf-8') as f:
                cache_data = json.load(f)
                if time.time() - cache_data["timestamp"] < 86400:  # 24 horas
                    return cache_data["results"]
        except (json.JSONDecodeError, KeyError):
            return None
    return None


def save_to_cache(search_query: str, result_data: List[Dict[str, str]]) -> None:
    """Salva os resultados no cache"""
    cache_file = get_cache_filename(search_query)
    with open(cache_file, "w", encoding='utf-8') as f:
        json.dump({
            "timestamp": time.time(),
            "results": result_data
        }, f, ensure_ascii=False)


# --- Funções de Processamento ---
def is_valid_link(url: str) -> bool:
    """Verifica se o link é válido"""
    blacklist = ["google", "facebook", "twitter", "youtube"]
    parsed = urlparse(url)
    return (
            parsed.scheme in ('http', 'https') and
            not any(domain in parsed.netloc.lower() for domain in blacklist) and
            not parsed.path.lower().endswith((".exe", ".zip"))
    )


def get_domain_type(url: str) -> str:
    """Classifica o domínio como Acadêmico ou Geral"""
    academic_domains = ['.edu', '.ac.', 'arxiv.org', 'scholar', 'research', 'ncbi', 'springer', 'ieee']
    return "Academic" if any(d in urlparse(url).netloc.lower() for d in academic_domains) else "General"


def enhance_query(base_query: str, search_type: str, file_type: Optional[str] = None,
                  site: Optional[str] = None) -> str:
    """Aprimora a query com operadores de busca"""
    academic_operators = ' intitle:"paper" OR intitle:"study" OR site:.edu OR site:.ac OR site:arxiv.org'

    enhanced = base_query
    if search_type == "File" and file_type:
        enhanced = f'filetype:{file_type} {enhanced}'
    elif search_type == "Specific Site" and site:
        enhanced = f'site:{site} {enhanced}'

    return enhanced + academic_operators


# --- Implementação da Busca com Cache e User Agent ---
def perform_search(query: str, num_results: int = 50) -> List[Dict[str, str]]:
    """Executa a busca com User Agent aleatório e cache"""
    cached = get_cached_results(query)
    if cached:
        return cached

    try:
        user_agent = random.choice(USER_AGENTS)
        # Versão modificada que remove os parâmetros não suportados
        search_results = google_search(
            query,
            num=num_results,  # Usando o parâmetro correto 'num' em vez de 'num_results'
            stop=num_results,  # Garante que não retorne mais que o solicitado
            pause=2.0,  # Adiciona pausa entre requisições
            user_agent=user_agent
        )

        processed = []
        for result in search_results:
            # Adaptação para o formato de retorno diferente
            if isinstance(result, str):  # Se for apenas a URL
                processed.append({
                    'url': result,
                    'title': 'No title',
                    'description': 'No description',
                    'type': get_domain_type(result)
                })
            else:  # Se for um objeto com atributos
                if hasattr(result, 'url') and is_valid_link(result.url):
                    processed.append({
                        'url': result.url,
                        'title': getattr(result, 'title', 'No title'),
                        'description': getattr(result, 'description', 'No description'),
                        'type': get_domain_type(result.url)
                    })

        save_to_cache(query, processed)
        return processed

    except Exception as e:
        st.error(f"Erro na busca: {str(e)}")
        return []


# --- Configuração do Streamlit ---
st.set_page_config(page_title="🔍 Academic Search Pro", layout="wide")
st.title("🔍 Academic Search Pro")

# CSS aprimorado
st.markdown("""
<style>
    .result-card {border: 1px solid #eee; padding: 1rem; margin-bottom: 1rem; border-radius: 5px;}
    .academic-badge {background: #4CAF50; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em;}
</style>
""", unsafe_allow_html=True)


# --- Interface Principal ---
def main():
    search_type = st.radio("Search type:", ["File", "Specific Site", "Custom"], horizontal=True)

    with st.form("smart_search_form"):
        query = ""

        if search_type == "File":
            file_type = st.selectbox("File type:", ["pdf", "docx", "xlsx", "pptx", "txt"])
            subject = st.text_input("Subject/keywords:", placeholder="e.g., machine learning algorithms")
            if subject:
                query = subject

        elif search_type == "Specific Site":
            site = st.text_input("Site/domain:", placeholder="e.g., mit.edu")
            subject = st.text_input("Subject/keywords:", placeholder="e.g., quantum computing")
            if site and subject:
                query = subject
        else:
            query = st.text_input("Enter your query:", placeholder="e.g., deep learning applications")

        # Opções avançadas
        with st.expander("Academic Filters"):
            lang = st.text_input("Language (e.g., en, pt):", max_chars=2)
            min_year = st.number_input("Minimum year:", min_value=1990, max_value=2023, value=2018)

        submitted = st.form_submit_button("🔍 Smart Search")

    # --- Processamento Inteligente ---
    if submitted and query:
        # Aprimora a query
        enhanced_query = enhance_query(
            query,
            search_type,
            file_type if search_type == "File" else None,
            site if search_type == "Specific Site" else None
        )

        if lang:
            enhanced_query += f" after:{min_year} lang:{lang}"

        st.code(f"🧠 Enhanced query: {enhanced_query}", language="markdown")

        # Executa a busca
        with st.spinner("🔍 Searching academic sources..."):
            search_results = perform_search(enhanced_query)

            if search_results:
                st.session_state.all_results = search_results
                st.session_state.current_page = 0
                st.success(f"Found {len(search_results)} relevant results")
            else:
                st.warning("No results found or error occurred")

    # --- Exibição Inteligente ---
    if 'all_results' in st.session_state and st.session_state.all_results:
        display_results(st.session_state.all_results)


def display_results(results: List[Dict[str, str]]) -> None:
    """Exibe os resultados da busca com paginação"""
    # Filtro
    col1, col2 = st.columns([3, 1])
    with col2:
        filter_type = st.selectbox("Filter results:", ["All", "Academic only", "General only"])

    filtered_results = [
        r for r in results
        if filter_type == "All" or
           (filter_type == "Academic only" and r['type'] == "Academic") or
           (filter_type == "General only" and r['type'] == "General")
    ]

    # Paginação
    results_per_page= 5
    total_pages = (len(filtered_results) // results_per_page) + 1
    current_page = st.session_state.get('current_page', 0)
    start_idx = current_page * results_per_page
    end_idx = start_idx + results_per_page

    # Mostrar resultados
    st.subheader(f"📚 Results ({len(filtered_results)} filtered)")

    for result in filtered_results[start_idx:end_idx]:
        with st.container():
            st.markdown(f"### {result['title']}")
            if result['type'] == "Academic":
                st.markdown(f"<span class='academic-badge'>Academic Source</span>", unsafe_allow_html=True)
            st.markdown(f"[{result['url']}]({result['url']})")
            st.write(result['description'])
            st.divider()

    # Controles de paginação
    col_prev, col_info, col_next = st.columns([1, 3, 1])
    with col_prev:
        if st.button("Previous", disabled=(current_page == 0)):
            st.session_state.current_page -= 1
            st.rerun()
    with col_info:
        st.markdown(f"Page {current_page + 1} of {total_pages}")
    with col_next:
        if st.button("Next", disabled=(end_idx >= len(filtered_results))):
            st.session_state.current_page += 1
            st.rerun()

    # Análise visual
    st.subheader("📊 Academic Insights")
    tab1, tab2 = st.tabs(["Domain Distribution", "Content Cloud"])

    with tab1:
        domains = [urlparse(r['url']).netloc for r in results]
        domain_counts = Counter(domains).most_common(10)
        df = pd.DataFrame(domain_counts, columns=["Domain", "Count"])
        st.bar_chart(df.set_index("Domain"))

    with tab2:
        text = ' '.join([r['title'] + ' ' + r['description'] for r in results])
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)


if __name__ == "__main__":
    main()