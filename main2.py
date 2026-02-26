import streamlit as st
import pandas as pd
import plotly.express as px
import os
import openpyxl

st.set_page_config(layout="wide", page_title="Dashboard Connect")

# =========================
# CONFIG VISUAL (CSS)
# =========================

st.markdown("""
<style>
.kpi-card {
    background-color: #1f2937;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
}
.kpi-title {
    font-size: 14px;
    color: #9ca3af;
}
.kpi-value {
    font-size: 32px;
    font-weight: bold;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 Dashboard Connect")

# =========================
# CARREGAR DADOS
# =========================

arquivo = "dados_connect_.xlsx"

df_participantes = pd.read_excel(arquivo, sheet_name="d_participantes")
df_presenca = pd.read_excel(arquivo, sheet_name="f_presenca_connect")
df_info = pd.read_excel(arquivo, sheet_name="f_connect_info")

df_presenca["data"] = pd.to_datetime(df_presenca["data"])
df_info["data"] = pd.to_datetime(df_info["data"])

# Base analítica
df = (
    df_presenca
    .merge(df_participantes, on="participantes", how="left")
    .merge(df_info, on="data", how="left")
)

# =========================
# FILTROS LATERAIS
# =========================

st.sidebar.header("Filtros")

data_range = st.sidebar.date_input(
    "Selecione intervalo de datas",
    value=[df["data"].min().date(), df["data"].max().date()], format='DD-MM-YYYY'
)

#ministro = st.sidebar.multiselect(
#    "Ministro",
#    df["ministro"].dropna().unique()
#)
#
#bairro = st.sidebar.multiselect(
#    "Bairro",
#    df["bairro"].dropna().unique()
#)
#
#local = st.sidebar.multiselect(
#3    "Local (Proprietário)",
#    df["prop_local"].dropna().unique()
#)

# Aplicar filtros

if len(data_range) == 2:
    df = df[(df["data"] >= pd.to_datetime(data_range[0])) &
            (df["data"] <= pd.to_datetime(data_range[1]))]

#if ministro:
#    df = df[df["ministro"].isin(ministro)]
#
#if bairro:
#    df = df[df["bairro"].isin(bairro)]
#
#if local:
#    df = df[df["prop_local"].isin(local)]


# =========================
# KPIs
# =========================

# Separações
df_adultos = df[df["tipo"] == "adulto"]
df_criancas = df[df["tipo"].isin(["kids", "teen", "baby"])]

# Totais
total_adultos_unicos = df_adultos["participantes"].nunique()
total_criancas_unicos = df_criancas["participantes"].nunique()
total_encontros = df["data"].nunique()

# Média presença ADULTOS
media_presenca_adultos = (
    df_adultos[df_adultos["presenca"] == "presente"]
    .groupby("data")
    .size()
    .mean()
)

# Taxa presença ADULTOS
taxa_presenca_adultos = (
    len(df_adultos[df_adultos["presenca"] == "presente"]) /
    len(df_adultos) * 100
    if len(df_adultos) > 0 else 0
)

col1, col2, col3, col4, col5 = st.columns(5)

col1.markdown(f"""
<div class="kpi-card">
<div class="kpi-title">Participantes (Adultos)</div>
<div class="kpi-value">{total_adultos_unicos}</div>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div class="kpi-card">
<div class="kpi-title">Crianças (Kids/Teen/Baby)</div>
<div class="kpi-value">{total_criancas_unicos}</div>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div class="kpi-card">
<div class="kpi-title">Encontros</div>
<div class="kpi-value">{total_encontros}</div>
</div>
""", unsafe_allow_html=True)

col4.markdown(f"""
<div class="kpi-card">
<div class="kpi-title">Média Presença (Adultos)</div>
<div class="kpi-value">{round(media_presenca_adultos,1) if media_presenca_adultos else 0}</div>
</div>
""", unsafe_allow_html=True)

col5.markdown(f"""
<div class="kpi-card">
<div class="kpi-title">Taxa Presença (Adultos %)</div>
<div class="kpi-value">{round(taxa_presenca_adultos,1)}%</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# =========================
# GRÁFICOS
# =========================

col_g1, col_g2 = st.columns(2)

# Evolução presença
presenca_tempo = (
    df[df["presenca"] == "presente"]
    .groupby("data")
    .size()
    .reset_index(name="Qtd")
)

fig1 = px.line(
    presenca_tempo,
    x="data",
    y="Qtd",
    markers=True,
    text="Qtd"
)

fig1.update_traces(
    textposition="top center",
    textfont=dict(size=14, color="black"),
    line=dict(width=3)
)

fig1.update_layout(
    title=dict(
        text="<b>Evolução de Presença</b>",
        x=0.02
    ),
    xaxis_title="<b>Data</b>",
    yaxis_title="<b>Quantidade</b>",
    title_font=dict(size=20),
    font=dict(size=14),
    margin=dict(l=40, r=40, t=60, b=40),
    hoverlabel=dict(font_size=14),
)

fig1.update_xaxes(
    showgrid=False
)

fig1.update_yaxes(
    showgrid=True,
    gridcolor="rgba(200,200,200,0.3)"
)

col_g1.plotly_chart(fig1, use_container_width=True)

# Presença por tipo AGRUPADO POR DATA
presenca_tipo = (
    df[df["presenca"] == "presente"]
    .groupby(["data", "tipo"])
    .size()
    .reset_index(name="Qtd")
)

fig2 = px.bar(
    presenca_tipo,
    x="data",
    y="Qtd",
    color="tipo",
    barmode="group",
    text="Qtd",
    color_discrete_map={
        "adulto": "#374151",   # cinza escuro elegante
        "kids": "#9CA3AF",     # cinza médio
        "teen": "#6B7280",     # cinza grafite
        "baby": "#D1D5DB"      # cinza claro
    }
)

fig2.update_traces(
    textposition="outside",
    textfont=dict(size=14, color="black"),
    marker_line_width=1.2
)

fig2.update_layout(
    title=dict(
        text="<b>Distribuição de Presença por Tipo e Data</b>",
        x=0.02
    ),
    xaxis_title="<b>Data</b>",
    yaxis_title="<b>Quantidade</b>",
    title_font=dict(size=20),
    font=dict(size=14),
    uniformtext_minsize=10,
    uniformtext_mode="hide",
    margin=dict(l=40, r=40, t=70, b=60),
    legend_title_text="<b>Tipo</b>"
)

# 🔥 Corrige corte dos valores (como você já fazia)
fig2.update_yaxes(
    range=[0, presenca_tipo["Qtd"].max() * 1.25]
)

fig2.update_xaxes(
    showgrid=False,
    tickformat="%d-%m-%Y"  # mantém padrão brasileiro
)

col_g2.plotly_chart(fig2, use_container_width=True)

st.markdown("---")









# =========================
# 📊 RESUMO DOS ENCONTROS
# =========================

st.markdown("### 📊 Resumo Executivo dos Encontros")

# Base apenas presentes
df_presentes = df[df["presenca"] == "presente"].copy()

if df_presentes.empty:
    st.warning("Nenhum encontro encontrado para o filtro selecionado.")
else:

    # Quantidade presentes por data
    resumo_presenca = (
        df_presentes
        .groupby("data")
        .agg(
            qtd_presentes_adultos=("tipo", lambda x: (x == "adulto").sum()),
            qtd_criancas=("tipo", lambda x: x.isin(["kids","teen","baby"]).sum()),
            qtd_visitantes=("obs", lambda x: (x == "visitante").sum())
        )
        .reset_index()
    )

    # Informações do encontro (1 registro por data)
    info_encontro = (
        df_info
        .drop_duplicates("data")[
            [
                "data",
                "dinamica",
                "tema_dinamica",
                "ministro",
                "tema_ministracao",
                "versiculo_base",
                "prop_local"
            ]
        ]
    )

    # Merge final
    resumo_final = resumo_presenca.merge(
        info_encontro,
        on="data",
        how="left"
    )

    # Formatando data
    resumo_final["data"] = resumo_final["data"].dt.strftime("%d-%m-%Y")

    # Ordenando
    resumo_final = resumo_final.sort_values("data", ascending=False)

    st.dataframe(
        resumo_final,
        use_container_width=True,
        hide_index=True
    )

st.markdown("---")








# =========================
# TABELA "QUEM ESTEVE PRESENTE"
# =========================

st.subheader("Quem esteve presente")

if df_presentes.empty:
    st.warning("Nenhum participante encontrado para o filtro selecionado.")
else:
    tabela_final = (
        df_presentes
        .sort_values("data", ascending=False)
        .assign(data=lambda x: x["data"].dt.strftime("%d-%m-%Y"))
        [["data", "participantes", "tipo"]]
    )

    st.dataframe(
        tabela_final,
        use_container_width=True,
        hide_index=True  # ✅ Remove índice lateral
    )

st.markdown("---")


# st.subheader("📸 Fotos dos Encontros")
# Pegar apenas fotos dos encontros filtrados
#fotos_df = df_presentes[["data", "foto_url"]].dropna().drop_duplicates()
#
#if fotos_df.empty:
#    st.info("Nenhuma foto disponível para o filtro selecionado.")
#else:
#    
#    for _, row in fotos_df.iterrows():
#        data_formatada = pd.to_datetime(row["data"]).strftime("%d-%m-%Y")
#        
#        st.markdown(f"**Encontro - {data_formatada}**")
#        st.image(row["foto_url"], use_container_width=True)
#










# =========================
# MAPA
# =========================

st.subheader("📍 Local dos Encontros")

mapa_df = df[["latitude", "longitude", "bairro"]].dropna().drop_duplicates()

if not mapa_df.empty:
    st.map(mapa_df.rename(columns={
        "latitude": "lat",
        "longitude": "lon"
    }))
else:
    st.warning("Sem coordenadas disponíveis para o filtro selecionado.")

st.markdown("---")











# =========================
# 📸 FOTOS DOS ENCONTROS (DINÂMICO)
# =========================

st.subheader("📸 Fotos dos Encontros")

# Datas únicas filtradas (ainda como datetime)
datas_filtro = df["data"].dropna().unique()

# Converter para formato dd-mm-aaaa
datas_formatadas = sorted(
    pd.to_datetime(datas_filtro).strftime("%d-%m-%Y")
)

if not datas_formatadas:
    st.warning("Nenhuma data encontrada para o filtro selecionado.")

else:

    # Layout em 3 colunas estilo galeria
    cols = st.columns(3)

    contador = 0

    for data_str in datas_formatadas:

        caminho_foto = f"assets/fotos_encontros/{data_str}.jpeg"

        if os.path.exists(caminho_foto):

            with cols[contador % 3]:
                st.image(
                    caminho_foto,
                    caption=f"Encontro - {data_str}",
                    use_container_width=True
                )

            contador += 1

    if contador == 0:
        st.info("Nenhuma foto encontrada para as datas filtradas.")


st.markdown("---")

