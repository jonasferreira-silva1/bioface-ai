"""
Dashboard Streamlit para BioFace AI.

Interface web para visualização e gerenciamento do sistema.
"""

import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
from typing import Optional

# Configuração da página
st.set_page_config(
    page_title="BioFace AI Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL da API (configurável)
API_BASE_URL = st.sidebar.text_input(
    "URL da API",
    value="http://localhost:8000",
    help="URL base da API FastAPI"
)

# Título
st.title("🧠 BioFace AI Dashboard")
st.markdown("Sistema de Reconhecimento Facial e Análise Comportamental")

# Sidebar
st.sidebar.title("Navegação")
page = st.sidebar.selectbox(
    "Escolha uma página",
    ["📊 Visão Geral", "👥 Usuários", "😊 Emoções", "📈 Estatísticas"]
)


def get_api(url: str) -> Optional[dict]:
    """Faz requisição GET à API."""
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao conectar com API: {e}")
        return None


def post_api(url: str, data: dict) -> Optional[dict]:
    """Faz requisição POST à API."""
    try:
        response = requests.post(url, json=data, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao enviar dados: {e}")
        return None


# Página: Visão Geral
if page == "📊 Visão Geral":
    st.header("Visão Geral do Sistema")
    
    # Health check
    health = get_api(f"{API_BASE_URL}/api/health")
    
    if health:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Status", "🟢 Online" if health.get("status") == "healthy" else "🔴 Offline")
        
        with col2:
            st.metric("Usuários", health.get("users_count", 0))
        
        with col3:
            st.metric("Conexões WebSocket", health.get("websocket_connections", 0))
        
        with col4:
            db_status = "🟢 Conectado" if health.get("database") == "connected" else "🔴 Desconectado"
            st.metric("Banco de Dados", db_status)
    
    # Estatísticas
    st.subheader("Estatísticas Gerais")
    stats = get_api(f"{API_BASE_URL}/api/stats")
    
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Usuários", stats.get("total_users", 0))
        
        with col2:
            st.metric("Usuários Ativos", stats.get("active_users", 0))
        
        with col3:
            st.metric("Total de Embeddings", stats.get("total_embeddings", 0))
        
        with col4:
            st.metric("Logs de Emoções", stats.get("total_emotion_logs", 0))
        
        # Distribuição de emoções
        if stats.get("emotions_distribution"):
            st.subheader("Distribuição de Emoções")
            emotions_data = stats["emotions_distribution"]
            
            if emotions_data:
                df_emotions = pd.DataFrame(
                    list(emotions_data.items()),
                    columns=["Emoção", "Quantidade"]
                )
                
                fig = px.pie(
                    df_emotions,
                    values="Quantidade",
                    names="Emoção",
                    title="Distribuição de Emoções Detectadas"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Atividade recente
        if stats.get("recent_activity"):
            st.subheader("Atividade Recente (24h)")
            activity = stats["recent_activity"]
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Emoções (24h)", activity.get("emotions_last_24h", 0))
            with col2:
                st.metric("Usuários Ativos (24h)", activity.get("users_active_last_24h", 0))


# Página: Usuários
elif page == "👥 Usuários":
    st.header("Gerenciamento de Usuários")
    
    # Criar novo usuário
    with st.expander("➕ Criar Novo Usuário"):
        user_name = st.text_input("Nome do usuário (opcional)", key="new_user_name")
        
        if st.button("Criar Usuário"):
            data = {"name": user_name if user_name else None}
            result = post_api(f"{API_BASE_URL}/api/users", data)
            
            if result:
                st.success(f"Usuário criado com sucesso! ID: {result.get('id')}")
                st.rerun()
    
    # Lista de usuários
    st.subheader("Usuários Cadastrados")
    
    users_data = get_api(f"{API_BASE_URL}/api/users?limit=1000")
    
    if users_data and users_data.get("users"):
        users = users_data["users"]
        
        # Tabela de usuários
        df_users = pd.DataFrame([
            {
                "ID": u["id"],
                "Nome": u["name"] or "Anônimo",
                "Embeddings": u["embeddings_count"],
                "Criado em": datetime.fromisoformat(u["created_at"].replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M"),
                "Ativo": "✅" if u["is_active"] else "❌"
            }
            for u in users
        ])
        
        st.dataframe(df_users, use_container_width=True, hide_index=True)
        
        # Detalhes de um usuário
        st.subheader("Detalhes do Usuário")
        user_ids = [u["id"] for u in users]
        selected_user_id = st.selectbox("Selecione um usuário", user_ids)
        
        if selected_user_id:
            user_details = get_api(f"{API_BASE_URL}/api/users/{selected_user_id}")
            
            if user_details:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**ID:** {user_details['id']}")
                    st.write(f"**Nome:** {user_details['name'] or 'Anônimo'}")
                    st.write(f"**Embeddings:** {user_details['embeddings_count']}")
                
                with col2:
                    st.write(f"**Status:** {'✅ Ativo' if user_details['is_active'] else '❌ Inativo'}")
                    created = datetime.fromisoformat(user_details['created_at'].replace("Z", "+00:00"))
                    st.write(f"**Criado em:** {created.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        st.info("Nenhum usuário cadastrado ainda.")


# Página: Emoções
elif page == "😊 Emoções":
    st.header("Histórico de Emoções")
    
    # Filtros
    col1, col2 = st.columns(2)
    
    with col1:
        user_filter = st.selectbox(
            "Filtrar por usuário",
            ["Todos"] + [f"Usuário {i}" for i in range(1, 100)],  # Simplificado
            key="emotion_user_filter"
        )
    
    with col2:
        limit = st.slider("Número de registros", 10, 1000, 100)
    
    # Buscar histórico
    url = f"{API_BASE_URL}/api/emotions/history?limit={limit}"
    if user_filter != "Todos":
        user_id = int(user_filter.split()[-1])
        url += f"&user_id={user_id}"
    
    emotions_data = get_api(url)
    
    if emotions_data and emotions_data.get("emotions"):
        emotions = emotions_data["emotions"]
        
        # Tabela
        df_emotions = pd.DataFrame([
            {
                "ID": e["id"],
                "Usuário": e["user_id"] or "Anônimo",
                "Emoção": e["emotion"],
                "Confiança": f"{e['confidence']:.2%}",
                "Timestamp": datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")
            }
            for e in emotions
        ])
        
        st.dataframe(df_emotions, use_container_width=True, hide_index=True)
        
        # Gráfico temporal
        if len(emotions) > 1:
            st.subheader("Evolução Temporal das Emoções")
            
            df_temporal = pd.DataFrame([
                {
                    "Timestamp": datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00")),
                    "Emoção": e["emotion"],
                    "Confiança": e["confidence"]
                }
                for e in emotions
            ])
            
            fig = px.line(
                df_temporal,
                x="Timestamp",
                y="Confiança",
                color="Emoção",
                title="Confiança das Emoções ao Longo do Tempo"
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhum registro de emoção encontrado.")


# Página: Estatísticas
elif page == "📈 Estatísticas":
    st.header("Estatísticas Detalhadas")
    
    stats = get_api(f"{API_BASE_URL}/api/stats")
    
    if stats:
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Usuários", stats.get("total_users", 0))
        
        with col2:
            st.metric("Usuários Ativos", stats.get("active_users", 0))
        
        with col3:
            st.metric("Total de Embeddings", stats.get("total_embeddings", 0))
        
        with col4:
            st.metric("Logs de Emoções", stats.get("total_emotion_logs", 0))
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            if stats.get("emotions_distribution"):
                st.subheader("Distribuição de Emoções")
                emotions_data = stats["emotions_distribution"]
                
                df_emotions = pd.DataFrame(
                    list(emotions_data.items()),
                    columns=["Emoção", "Quantidade"]
                )
                
                fig = px.bar(
                    df_emotions,
                    x="Emoção",
                    y="Quantidade",
                    title="Quantidade por Emoção"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if stats.get("recent_activity"):
                st.subheader("Atividade Recente")
                activity = stats["recent_activity"]
                
                df_activity = pd.DataFrame([
                    {"Métrica": "Emoções (24h)", "Valor": activity.get("emotions_last_24h", 0)},
                    {"Métrica": "Usuários Ativos (24h)", "Valor": activity.get("users_active_last_24h", 0)}
                ])
                
                fig = px.bar(
                    df_activity,
                    x="Métrica",
                    y="Valor",
                    title="Atividade nas Últimas 24 Horas"
                )
                st.plotly_chart(fig, use_container_width=True)

# Rodapé
st.sidebar.markdown("---")
st.sidebar.markdown("**BioFace AI v1.0.0**")
st.sidebar.markdown("Sistema de Reconhecimento Facial")

