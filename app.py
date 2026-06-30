import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página do Streamlit
st.set_page_config(page_title="Dashboard ENEM: Unidades vs Benchmark", layout="wide")

# Função para carregar os dados
@st.cache_data
def load_data():
    # Carrega o CSV usando o separador ponto e vírgula
    df = pd.read_csv("ENEM_comparacao_Final.csv", sep=",")
    return df

df = load_data()

# Separar o Benchmark Original (Público)
benchmark_name = "benchmark"
df_benchmark = df[df['MASCARA'] == benchmark_name].iloc[0]

# DataFrame com todas as outras máscaras (excluindo o benchmark público)
df_escolas = df[df['MASCARA'] != benchmark_name]

# Calcular o Benchmark Médio (Média de todas as máscaras EXCETO o benchmark público)
benchmark_medio = df_escolas.mean(numeric_only=True)


st.title("📊 Dashboard de Desempenho ENEM")

# Filtro por MASCARA movido para o topo do Dashboard
mascara_selecionada = st.selectbox(
    "Selecione uma escola para visualizar em destaque nos gráficos:",
    options=df_escolas['MASCARA'].unique()
)

# Filtrar os dados da máscara selecionada
dados_selecionados = df_escolas[df_escolas['MASCARA'] == mascara_selecionada].iloc[0]

st.markdown(f"**Comparando:** `{mascara_selecionada}` 🆚 `{benchmark_name}` 🆚 `Média das Demais Escolas`")
st.divider()

col1, col2, col3, col4 = st.columns(4)

with col1:
    delta_global = dados_selecionados['Media_MEDIA_GLOBAL'] - df_benchmark['Media_MEDIA_GLOBAL']
    st.metric(label="Média Global", 
              value=f"{dados_selecionados['Media_MEDIA_GLOBAL']:.2f}", 
              delta=f"{delta_global:.2f} vs Benchmark Público")

with col2:
    delta_redacao = dados_selecionados['Media_NU_NOTA_REDACAO'] - df_benchmark['Media_NU_NOTA_REDACAO']
    st.metric(label="Média Redação", 
              value=f"{dados_selecionados['Media_NU_NOTA_REDACAO']:.2f}", 
              delta=f"{delta_redacao:.2f} vs Benchmark Público")

with col3:
    st.metric(label="Mensalidade", 
              value=f"R$ {dados_selecionados['MENSALIDADE']:.2f}")

with col4:
    st.metric(label="Taxa de Cobertura (%)", 
              value=f"{dados_selecionados['TAXA_COBERTURA_PCT']:.2f}%")

st.write("---")

# ==========================================
# VISUALIZAÇÕES
# ==========================================
col_grafico1, col_grafico2 = st.columns(2)

with col_grafico1:
    st.subheader("Radar de Desempenho (Notas)")
    
    categorias = ['Média Global', 'Média Objetivas', 'Média Redação']
    
    fig_radar = go.Figure()
    
    # 1. Adiciona a máscara selecionada
    fig_radar.add_trace(go.Scatterpolar(
        r=[dados_selecionados['Media_MEDIA_GLOBAL'], dados_selecionados['Media_MEDIA_OBJETIVAS'], dados_selecionados['Media_NU_NOTA_REDACAO']],
        theta=categorias,
        fill='toself',
        name=mascara_selecionada,
        line_color='blue'
    ))
    
    # 2. Adiciona o benchmark público
    fig_radar.add_trace(go.Scatterpolar(
        r=[df_benchmark['Media_MEDIA_GLOBAL'], df_benchmark['Media_MEDIA_OBJETIVAS'], df_benchmark['Media_NU_NOTA_REDACAO']],
        theta=categorias,
        fill='toself',
        name='Benchmark (Públicas)',
        line_color='red'
    ))

    # 3. Adiciona o Benchmark Médio (Média de todas menos públicas)
    fig_radar.add_trace(go.Scatterpolar(
        r=[benchmark_medio['Media_MEDIA_GLOBAL'], benchmark_medio['Media_MEDIA_OBJETIVAS'], benchmark_medio['Media_NU_NOTA_REDACAO']],
        theta=categorias,
        fill='toself',
        name='Média das Demais Escolas',
        line_color='green'
    ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, 
                range=[0, 1000],
                tickfont=dict(color='black')  #
            ),
            angularaxis=dict(
                tickfont=dict(color='orange')  
            )
        ),
        showlegend=True,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with col_grafico2:
    st.subheader("Custo vs Média Global (Todas as Escolas)")
    
    def classificar_ponto(nome):
        if nome == mascara_selecionada:
            return "Escola Selecionada"
        elif nome == benchmark_name:
            return "Benchmark Público"
        else:
            return "Outras Escolas"
            
    df_plot = df.copy()
    df_plot['Categoria'] = df_plot['MASCARA'].apply(classificar_ponto)
    
    # Ordenar para que a selecionada e o benchmark fiquem visíveis por cima
    df_plot['Ordem'] = df_plot['Categoria'].map({"Escola Selecionada": 2, "Benchmark Público": 1, "Outras Escolas": 0})
    df_plot = df_plot.sort_values('Ordem')
    
    fig_scatter = px.scatter(
        df_plot, 
        x="MENSALIDADE", 
        y="Media_MEDIA_GLOBAL",
        color="Categoria",
        size="NUM_ALUNOS",
        hover_name="MASCARA",
        color_discrete_map={
            "Escola Selecionada": "blue",
            "Benchmark Público": "red",
            "Outras Escolas": "lightgray"
        },
        labels={"MENSALIDADE": "Mensalidade (R$)", "Media_MEDIA_GLOBAL": "Média Global"}
    )
    
    fig_scatter.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_scatter, use_container_width=True)

st.write("---")


# ==========================================
# GRÁFICOS INFERIORES
# ==========================================
col_inferior1, col_inferior2 = st.columns(2)

with col_inferior1:
    st.subheader("Esforço Financeiro e Custo por Ponto")

    # Legenda manual ajustada
    st.markdown(
        "**Legenda:** "
        "🟦 Escola Selecionada | "
        "⬜ Outras Escolas"
    )

    df_todas = df.copy()
    
    metricas_financeiras = ['CUSTO_POR_PONTO_COBERTURA', 'ESFORCO_FINANC_MENSAL_POR_PONTO']
    df_bar = df_todas.melt(
        id_vars=['MASCARA'],
        value_vars=metricas_financeiras,
        var_name='Métrica',
        value_name='Valor'
    )

    # Criar o mapa de cores dinâmico baseado na MASCARA
    mapa_cores = {mascara: "lightgray" for mascara in df_todas['MASCARA']}
    mapa_cores[mascara_selecionada] = "blue"
    mapa_cores[benchmark_name] = "red"

    # Ordenar por Valor para que as barras formem um ranking descrescente
    df_bar = df_bar.sort_values(by='Valor', ascending=False)

    fig_bar = px.bar(
        df_bar, 
        x='Métrica', 
        y='Valor', 
        color='MASCARA', 
        barmode='group',
        color_discrete_map=mapa_cores,
        hover_name='MASCARA'
    )
    
    fig_bar.update_layout(
        yaxis_title="Valor (R$)", 
        xaxis_title="",
        margin=dict(t=10),
        showlegend=False 
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)
    
with col_inferior2:
    st.subheader("Ranking de Média Global (Todas as Escolas)")
    
    # Prepara os dados ranqueados
    df_ranking = df.sort_values(by="Media_MEDIA_GLOBAL", ascending=False)
    
    df_ranking['Categoria'] = df_ranking['MASCARA'].apply(classificar_ponto)
    
    fig_ranking = px.bar(
        df_ranking,
        x="MASCARA",
        y="Media_MEDIA_GLOBAL",
        color="Categoria",
        color_discrete_map={
            "Escola Selecionada": "blue",
            "Benchmark Público": "red",
            "Outras Escolas": "lightgray"
        },
        labels={"MASCARA": "Escola", "Media_MEDIA_GLOBAL": "Média Global"}
    )
    
    fig_ranking.update_layout(
        xaxis_tickangle=-45, 
        margin=dict(t=30),
        xaxis_title="",
        showlegend=False,
        xaxis={'categoryorder': 'total descending'} 
    )
    st.plotly_chart(fig_ranking, use_container_width=True)
    
    
st.write("---")
st.header("Análises Adicionais: Perfil de Notas e Entrega")

st.markdown(
    "**Legenda:** "
    "🟦 Escola Selecionada | "
    "🟥 Benchmark Público | "
    "⬜ Outras Escolas"
)

col_extra1, col_extra2 = st.columns(2)

# ==========================================
# GRÁFICO 1: REDAÇÃO VS OBJETIVAS
# ==========================================
with col_extra1:
    st.subheader("Perfil: Redação vs Objetivas")
    st.caption("Identifica se a instituição tem ensino equilibrado ou se depende da Redação para elevar a média global.")
    
    df_extra = df.copy()
    df_extra['Categoria'] = df_extra['MASCARA'].apply(classificar_ponto)
    
    df_extra['Ordem'] = df_extra['Categoria'].map({"Escola Selecionada": 2, "Benchmark Público": 1, "Outras Escolas": 0})
    df_extra = df_extra.sort_values('Ordem')
    
    fig_obj_red = px.scatter(
        df_extra,
        x="Media_MEDIA_OBJETIVAS",
        y="Media_NU_NOTA_REDACAO",
        color="Categoria",
        size="NUM_ALUNOS",
        hover_name="MASCARA",
        color_discrete_map={
            "Escola Selecionada": "blue",
            "Benchmark Público": "red",
            "Outras Escolas": "lightgray"
        },
        labels={
            "Media_MEDIA_OBJETIVAS": "Média nas Provas Objetivas", 
            "Media_NU_NOTA_REDACAO": "Média na Redação"
        }
    )
    fig_obj_red.update_layout(margin=dict(l=20, r=20, t=30, b=20), showlegend=False)
    st.plotly_chart(fig_obj_red, use_container_width=True)

# ==========================================
# GRÁFICO 2: RANKING DE TAXA DE COBERTURA
# ==========================================
with col_extra2:
    st.subheader("Ranking de Entrega (Taxa de Cobertura)")
    st.caption("Compara a porcentagem do conteúdo e simulados que foram efetivamente aplicados/cobertos.")
    
    df_cobertura = df_extra.sort_values(by="TAXA_COBERTURA_PCT", ascending=False)
    
    fig_cob = px.bar(
        df_cobertura,
        x="MASCARA",
        y="TAXA_COBERTURA_PCT",
        color="Categoria",
        color_discrete_map={
            "Escola Selecionada": "blue",
            "Benchmark Público": "red",
            "Outras Escolas": "lightgray"
        },
        labels={"MASCARA": "", "TAXA_COBERTURA_PCT": "Taxa de Cobertura (%)"}
    )
    fig_cob.update_layout(
        xaxis_tickangle=-45,
        margin=dict(t=30),
        showlegend=False,
        xaxis={'categoryorder': 'total descending'} 
    )
    st.plotly_chart(fig_cob, use_container_width=True)
    
st.write("---")
st.subheader("Correlação: Esforço Financeiro vs Cobertura de Cursos")
st.caption("Analisa se um maior esforço financeiro reflete em uma maior entrega real de conteúdo.")

df_corr = df.copy()
df_corr['Categoria'] = df_corr['MASCARA'].apply(classificar_ponto)

df_corr['Ordem'] = df_corr['Categoria'].map({"Escola Selecionada": 2, "Benchmark Público": 1, "Outras Escolas": 0})
df_corr = df_corr.sort_values('Ordem')

fig_corr = px.scatter(
    df_corr,
    x="NUM_CURSOS_COBERTOS", 
    y="ESFORCO_FINANC_MENSAL_POR_PONTO",
    color="Categoria",
    size="NUM_ALUNOS", 
    hover_name="MASCARA",
    color_discrete_map={
        "Escola Selecionada": "blue",
        "Benchmark Público": "red",
        "Outras Escolas": "lightgray"
    },
    labels={
        "NUM_CURSOS_COBERTOS": "Cobertura de cursos", 
        "ESFORCO_FINANC_MENSAL_POR_PONTO": "Esforço Financeiro por Ponto (R$)"
    }
)

fig_corr.update_layout(margin=dict(l=20, r=20, t=30, b=20), showlegend=False)
st.plotly_chart(fig_corr, use_container_width=True)

# Rodapé com a fonte de dados descaracterizada
st.caption(f"**Fonte dos dados da escola selecionada:** {dados_selecionados['FONTE']}")