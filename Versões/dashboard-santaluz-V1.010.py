import streamlit as st

import pandas as pd

import json

import urllib.request

import time

from datetime import datetime
import textwrap



# Config

TOKEN = st.secrets["PROCFY_TOKEN"]

BASE_URL = "https://api.procfy.io/api/v1/"

GLOSSARIO_INFO = {
    "CONTRIBUIÇÃO - CERIMÔNIAS": {"Tipo": "Recebimentos", "Descrição": "Entradas referentes às contribuições de cerimônias."},
    "MENSALIDADE - MANTENEDORES": {"Tipo": "Recebimentos", "Descrição": "Entradas referentes às mensalidades dos Mantenedores."},
    "CONTRIBUIÇÃO - EVENTOS": {"Tipo": "Recebimentos", "Descrição": "Entradas referentes às contribuições de eventos como festas, saraus, dentre outros."},
    "DOAÇÕES RECEBIDAS": {"Tipo": "Recebimentos", "Descrição": "Entradas referentes às doações recebidas."},
    "RATEIO - ALIMENTAÇÃO": {"Tipo": "Recebimentos", "Descrição": "Entradas referentes aos rateios de refeições. A SantaLuz efetuou o pagamento inicial e, posteriormente, recebeu a parte devida por cada um dos demais participantes."},
    "REPASSE DE MEDICINAS": {"Tipo": "Recebimentos", "Descrição": "Entradas referentes ao repasse de medicinas do estoque da Santaluz para outros centros.."},
    "RENDIMENTOS FINANCEIROS": {"Tipo": "Recebimentos", "Descrição": "Entradas referente a rendimentos de aplicações financeiras CDB."},
    "CONTRIBUIÇÃO - RETIROS": {"Tipo": "Recebimentos", "Descrição": "Entradas referentes às contribuições de retiros."},
    "RIFAS": {"Tipo": "Recebimentos", "Descrição": "Entradas referente às arrecadações realizadas por meio de rifas."},
    "ASSINATURA DE SERVIÇOS DIGITAIS": {"Tipo": "Despesas fixas", "Descrição": "Despesas com a assinatura de serviços digitais, como sistemas de gestão financeira."},
    "CONTABILIDADE": {"Tipo": "Despesas fixas", "Descrição": "Despesas com escritório de contabilidade."},
    "CONTRIBUIÇÃO PARA USO DO ESPAÇO E RECURSOS": {"Tipo": "Despesas fixas", "Descrição": "Essa despesa cobre o uso do espaço e outras comodidades, como internet, água e energia, além de uma contribuição para os gastos com os animais. O valor é repassado ao dirigente, proprietário do chacará onde a SantaLuz está localizada.."},
    "CUSTEIO DE VIAGEM": {"Tipo": "Despesas variáveis", "Descrição": "Ajuda de custos de viagens para transporte de artistas em apresentações na Santaluz, ou para a condução de cerimônias da SantaLuz em outros locais."},
    "APRESENTAÇÃO ARTÍSTICA": {"Tipo": "Despesas variáveis", "Descrição": "Custos associados a apresentações artísticas, incluindo a contratação de músicos para eventos comemorativos."},
    "REPASSE DE CERIMÔNIA DE TERCEIROS": {"Tipo": "Despesas variáveis", "Descrição": "Despesas relacionadas ao repasse de contribuições de cerimônias realizadas na Santaluz por coletivos externos, como indígenas, que serão destinadas a esses grupos.."},
    "AYAHUASCA": {"Tipo": "Despesas variáveis", "Descrição": "Despesa com a aquisição de medicina ayahuasca, o principal insumo para a realização das cerimônias na SantaLuz."},
    "DESPESAS COM RETIRO": {"Tipo": "Despesas variáveis", "Descrição": "Despesas relacionadas diretamente a organização e realização de retiros."},
    "DEVOLUÇÕES (DESISTÊNCIA)": {"Tipo": "Despesas variáveis", "Descrição": "Despesa referente à restituição de contribuições de cerimônias, aplicável quando um frequentador, após contribuir, informa antecipadamente sua impossibilidade de comparecimento."},
    "MANUTENÇÃO DE EQUIPAMENTOS": {"Tipo": "Despesas variáveis", "Descrição": "Despesas relacionadas à manutenção dos equipamentos da SantaLuz."},
    "MANUTENÇÃO DAS INSTALAÇÕES": {"Tipo": "Despesas variáveis", "Descrição": "Despesas relacionadas à manutenção das instalações da SantaLuz."},
    "LENHAS": {"Tipo": "Despesas variáveis", "Descrição": "Despesas relacionadas à aquisição de lenhas para a fogueira."},
    "MATERIAIS DE LIMPEZA": {"Tipo": "Despesas variáveis", "Descrição": "Despesas com materiais de limpeza."},
    "TARIFAS BANCÁRIAS": {"Tipo": "Despesas variáveis", "Descrição": "Despesas com tarifas bancárias e notificações de cobranças."},
    "INSTALAÇÕES": {"Tipo": "Despesas variáveis", "Descrição": "Investimentos realizados na melhoria das instalações."},
    "EQUIPAMENTOS , FERRAMENTAS E UTENSÍLIOS": {"Tipo": "Despesas variáveis", "Descrição": "Custos associados à compra de novos equipamentos, ferramentas e utensílios."},
    "DEMAIS DESPESAS": {"Tipo": "Despesas variáveis", "Descrição": "Outras despesas esporádicas e de baixo valor."},
    "RAPÉ / TABACO": {"Tipo": "Despesas variáveis", "Descrição": "Despesas com medicina do Rapé e Tabaco."},
    "VELAS": {"Tipo": "Despesas variáveis", "Descrição": "Despesas com Velas."},
    "ALIMENTOS E REFEIÇÕES": {"Tipo": "Despesas variáveis", "Descrição": "Despesas com alimentos e refeições referem-se à contrapartida mencionada na categoria de receitas \"Rateio de alimentação\". Neste processo, a SantaLuz efetua o pagamento e, posteriormente, recebe dos frequentadores o valor correspondente à parte devida por cada um."},
        "ANIMAIS": {"Tipo": "Despesas variáveis", "Descrição": "Custos com ração, vacinas, medicamentos e assistência veterinária. Conta descontinuada em setembro/2024, sendo unificada na categoria CONTRIBUIÇÃO PARA USO DO ESPAÇO E RECURSOS."},
    "ENERGIA ELÉTRICA": {"Tipo": "Despesas fixas", "Descrição": "Fornecimento e consumo de energia elétrica predial. Conta descontinuada em setembro/2024, sendo unificada na categoria CONTRIBUIÇÃO PARA USO DO ESPAÇO E RECURSOS."},
    "INTERNET": {"Tipo": "Despesas fixas", "Descrição": "Assinatura de serviços de conectividade e banda larga. Conta descontinuada em setembro/2024, sendo unificada na categoria CONTRIBUIÇÃO PARA USO DO ESPAÇO E RECURSOS."},
    "CHECKLIST": {"Tipo": "Despesas variáveis", "Descrição": "Esta categoria de despesa abrange um checklist de itens adquiridos regularmente para a realização das cerimônias, como saquinhos, papel higiênico,, ervas para tabaco e defumação, incensos, entre outros."}
}


SALDO_INICIAL_2023 = 10774.37



st.set_page_config(page_title="Dashboard SantaLuz", layout="wide", page_icon="✨")
st.markdown('''
<style>
@media print {
    section[data-testid="stSidebar"] { display: none !important; }
    header { display: none !important; }
    .stApp { background-color: white !important; }
    .block-container { max-width: 100% !important; padding: 10mm !important; }
    * { color: black !important; }
    .stPlotlyChart { page-break-inside: avoid; }
    table { page-break-inside: avoid; color: black !important; }
    th, td { color: black !important; }
    
    div[data-testid="stHorizontalBlock"] { display: block !important; }
    div[data-testid="column"] { width: 100% !important; max-width: 100% !important; display: block !important; margin-bottom: 20px !important; }
        .pagebreak { page-break-before: always !important; display: block !important; width: 100% !important; height: 1px !important; }
    iframe { display: none !important; }
    .no-print { display: none !important; }
}
</style>
''', unsafe_allow_html=True)




@st.cache_data(ttl=3600, show_spinner=False)

def fetch_categories():

    all_cats = {}

    page = 1

    while True:

        req = urllib.request.Request(f"{BASE_URL}categories?page={page}", headers={

            'Authorization': f'Bearer {TOKEN}',

            'Accept': 'application/json'

        })

        try:

            with urllib.request.urlopen(req) as response:

                data = json.loads(response.read().decode())

                cats = data.get('data', [])

                for c in cats:

                    all_cats[str(c['id'])] = c['name']

                

                total_pages = data.get('page', {}).get('pages', 1)

                if page >= total_pages:

                    break

                page += 1

        except Exception as e:

            st.error(f"Erro ao buscar categorias na página {page}: {e}")

            time.sleep(1)

            # break # Don't break, just stop trying if it fails too much

            break

    return all_cats



@st.cache_data(ttl=3600, show_spinner=False)

def fetch_all_transactions():

    all_data = []

    page = 1

    progress_text = "Atualizando dados da API. Isso pode levar um tempo para puxar desde 2024..."

    my_bar = st.progress(0, text=progress_text)

    

    total_pages = 1

    retries = 0

    

    while page <= total_pages:

        req = urllib.request.Request(f"{BASE_URL}transactions?per_page=100&page={page}", headers={

            'Authorization': f'Bearer {TOKEN}',

            'Accept': 'application/json'

        })

        try:

            with urllib.request.urlopen(req) as response:

                data = json.loads(response.read().decode())

                all_data.extend(data.get('data', []))

                

                total_pages = data.get('page', {}).get('pages', 1)

                

                progress = min(page / total_pages, 1.0)

                my_bar.progress(progress, text=f"Buscando página {page} de {total_pages} (Buscando desde 2024)...")

                

                page += 1

                retries = 0

        except Exception as e:

            retries += 1

            if retries > 3:

                st.error(f"Falha repetida na página {page}. Algumas transações podem faltar: {e}")

                break

            time.sleep(2)

            

    my_bar.empty()

    

    if not all_data:

        return pd.DataFrame()

        

    df = pd.DataFrame(all_data)

    

    # 1. Somente contas pagas

    df = df[df['paid'] == True]

    

    # Ignorar transferências e manter apenas receitas e despesas

    if 'transaction_type' in df.columns:

        df = df[df['transaction_type'].isin(['revenue', 'variable_expense', 'fixed_expense'])]

    

    # Converter category_id

    df['category_id_str'] = df['category_id'].fillna(0).astype(int).astype(str)

    df = df[df['category_id_str'] != '0']

    

    # Para bater exatamente com os relatórios gerados pelo Procfy em Excel,

    # precisamos usar a "Data" (que no sistema é due_date) para enquadrar no mês/ano.

    # A data de pagamento (paid_at) é usada para atestar que foi liquidado, 

    # mas o Procfy exporta e agrupa pelo due_date nos resumos mensais.

    df['due_date'] = pd.to_datetime(df['due_date'], errors='coerce')

    df = df.dropna(subset=['due_date'])

    

    # 2. Base de dados se inicia em 01/01/2024

    df = df[df['due_date'] >= pd.Timestamp('2024-01-01', tz=df['due_date'].dt.tz)]

    

    df['year'] = df['due_date'].dt.year

    df['month'] = df['due_date'].dt.month

    df['amount'] = df['amount'].astype(float)

    

    type_map = {

        'revenue': 'Receita',

        'variable_expense': 'Despesa Variável',

        'fixed_expense': 'Despesa Fixa'

    }

    df['type_pt'] = df['transaction_type'].map(type_map)

    

    return df



with st.spinner("Carregando dados completos da API..."):

    categories_map = fetch_categories()

    df_transactions = fetch_all_transactions()



if df_transactions.empty:

    st.warning("Nenhuma transação encontrada (após filtrar data >= 01/01/2024 e contas liquidadas).")

    st.stop()



df_transactions['category_name'] = df_transactions['category_id_str'].map(categories_map).fillna("Sem Categoria")



col_img1, col_img2, col_img3 = st.sidebar.columns([1, 2, 1])
col_img2.image("logo sta-luz.png", use_container_width=True)

if 'page' not in st.session_state:
    st.session_state.page = "Prestação de Contas Mensal"

st.sidebar.markdown("### Navegação")
if st.sidebar.button("Prestação de Contas Mensal", type="primary" if st.session_state.page == "Prestação de Contas Mensal" else "secondary", use_container_width=True):
    st.session_state.page = "Prestação de Contas Mensal"
    st.rerun()
if st.sidebar.button("Fluxo de Caixa Gerencial", type="primary" if st.session_state.page == "Fluxo de Caixa Gerencial" else "secondary", use_container_width=True):
    st.session_state.page = "Fluxo de Caixa Gerencial"
    st.rerun()
page = st.session_state.page

st.sidebar.markdown("---")





if page == "Prestação de Contas Mensal":
    st.title("📊 Dashboard Financeiro SantaLuz")
    st.markdown("Acompanhamento do fluxo financeiro e prestação de contas.")

    st.sidebar.header("Filtros")

    today = datetime.today()

    if today.month == 1:

        default_year = today.year - 1

        default_month = 12

    else:

        default_year = today.year

        default_month = today.month - 1

    

    years = sorted(df_transactions['year'].unique(), reverse=True)

    if not years:

        st.warning("Nenhum ano disponível.")

        st.stop()

        

    if 'selected_year' not in st.session_state:

        st.session_state.selected_year = default_year if default_year in years else years[0]

    if 'selected_month' not in st.session_state:

        st.session_state.selected_month = default_month

    

    st.sidebar.markdown("**Ano**")

    years_sorted = sorted(years)

    for i in range(0, len(years_sorted), 3):

        chunk = years_sorted[i:i+3]

        cols_y = st.sidebar.columns(3)

        for j, y in enumerate(chunk):

            is_sel = (st.session_state.selected_year == y)

            if cols_y[j].button(str(y), key=f"y_{y}", type="primary" if is_sel else "secondary", use_container_width=True):

                st.session_state.selected_year = y

                st.rerun()

    

    st.sidebar.markdown("**Mês**")

    month_abbr = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]

    for row in range(4):

        cols_m = st.sidebar.columns(3)

        for col in range(3):

            m_idx = row * 3 + col

            m_num = m_idx + 1

            m_name = month_abbr[m_idx]

            is_sel = (st.session_state.selected_month == m_num)

            if cols_m[col].button(m_name, key=f"m_{m_num}", type="primary" if is_sel else "secondary", use_container_width=True):

                st.session_state.selected_month = m_num

                st.rerun()

    

    selected_year = st.session_state.selected_year

    selected_month = st.session_state.selected_month

    

    # To keep month_mapping available for later use (e.g. Resumo do Mês title)

    months = list(range(1, 13))

    month_names = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

    month_mapping = dict(zip(months, month_names))

    

    if st.sidebar.button("🔄 Atualizar Dados da API"):

        fetch_categories.clear()

        fetch_all_transactions.clear()

        st.rerun()

    

    st.sidebar.markdown("---")

    st.sidebar.markdown("Dashboard desenvolvido para a comunidade SantaLuz.")

    

    # Saldo Inicial Computado

    df_historical = df_transactions[

        (df_transactions['year'] < selected_year) | 

        ((df_transactions['year'] == selected_year) & (df_transactions['month'] < selected_month))

    ]

    

    fluxo_historico = df_historical.apply(lambda row: row['amount'] if row['transaction_type'] == 'revenue' else -row['amount'], axis=1).sum()

    saldo_anterior = SALDO_INICIAL_2023 + fluxo_historico

    

    df_period = df_transactions[

        (df_transactions['year'] == selected_year) & 

        (df_transactions['month'] == selected_month)

    ].copy()

    

    df_receitas = df_period[df_period['transaction_type'] == 'revenue']

    df_despesas = df_period[df_period['transaction_type'].isin(['variable_expense', 'fixed_expense'])]

    

    total_receitas = df_receitas['amount'].sum()

    total_despesas = df_despesas['amount'].sum()

    balanco = total_receitas - total_despesas

    saldo_final = saldo_anterior + balanco

    

    st.header(f"Resumo do Mês: {month_mapping[selected_month]} | {selected_year}")

    

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:

        st.metric("Saldo Anterior", f"R$ {saldo_anterior:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    with col2:

        st.metric("Total Recebimentos", f"R$ {total_receitas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), delta=f"{len(df_receitas)} transações")

    with col3:

        st.metric("Total Despesas", f"R$ {-total_despesas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), delta=f"{len(df_despesas)} transações", delta_color="inverse")

    with col4:

        st.metric("Balanço no Período", f"R$ {balanco:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    with col5:

        st.metric("Saldo Final", f"R$ {saldo_final:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    

    st.markdown("---")

    

    import plotly.express as px

    

    colA, colB = st.columns(2)

    

    with colA:
        st.markdown('<div class="pagebreak"></div>', unsafe_allow_html=True)
        st.subheader("Receitas: De Onde Veio o Dinheiro?")

        if not df_receitas.empty:

            df_rec_grp = df_receitas.groupby('category_name')['amount'].sum().reset_index()

            

            # Group small slices into 'Outros' for the pie chart

            df_rec_grp_pie = df_rec_grp.rename(columns={'category_name': 'Categoria', 'amount': 'Valor'})

            

            df_rec_grp_pie['Categoria_Quebrada'] = df_rec_grp_pie['Categoria'].apply(lambda x: "<br>".join(textwrap.wrap(x, width=30)))
            fig_rec = px.pie(df_rec_grp_pie, values='Valor', names='Categoria_Quebrada', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_rec.update_traces(textposition='inside', textinfo='percent', domain=dict(x=[0, 1], y=[0.3, 1]), hovertemplate="<b>%{label}</b><br>Valor: R$ %{value:,.2f}<br>Participação: %{percent}<extra></extra>")
            fig_rec.update_layout(legend=dict(orientation="h", yanchor="top", y=0.2, xanchor="center", x=0.5), margin=dict(t=20, b=0, l=0, r=0), height=500)
            st.plotly_chart(fig_rec, use_container_width=True)

            

            df_rec_table = df_receitas.groupby('category_name').agg(Quantidade=('id', 'count'), Valor=('amount', 'sum')).reset_index()
            df_rec_table = df_rec_table.sort_values(by='Valor', ascending=False)
            html_t = "<div style='overflow-x:auto;'><table style='width:100%; border-collapse: collapse; text-align: left; font-size: 14px;'>"
            html_t += "<tr style='border-bottom: 2px solid #aaa;'><th style='padding: 8px;'>Categoria</th><th style='padding: 8px; text-align:right;'>Porcentagem</th><th style='padding: 8px; width: 100px;'>Valor</th></tr>"
            for _, row in df_rec_table.iterrows():
                pct = f"{(row['Valor'] / total_receitas * 100):.2f}%"
                val_str = f"{row['Valor']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                html_t += f"<tr style='border-bottom: 1px solid #ddd;'><td style='padding: 8px;'>{row['category_name']}</td><td style='padding: 8px; text-align:right;'>{pct}</td><td style='padding: 8px;'><div style='display: flex; justify-content: space-between; width: 85px; margin-left: auto;'><span>R$</span><span style='white-space: nowrap;'>{val_str}</span></div></td></tr>"
            total_val_str = f"{total_receitas:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            html_t += f"<tr style='font-weight: bold; color: #27ae60; border-top: 2px solid #aaa;'><td style='padding: 8px;'>TOTAL RECEITAS</td><td style='padding: 8px; text-align:right;'>100.00%</td><td style='padding: 8px;'><div style='display: flex; justify-content: space-between; width: 85px; margin-left: auto;'><span>R$</span><span style='white-space: nowrap;'>{total_val_str}</span></div></td></tr>"
            html_t += "</table></div>"
            st.markdown(html_t, unsafe_allow_html=True)

        else:

            st.info("Nenhuma receita neste período.")

    

    with colB:
        st.markdown('<div class="pagebreak"></div>', unsafe_allow_html=True)
        st.subheader("Despesas: Para Onde Foi o Dinheiro?")

        if not df_despesas.empty:

            df_desp_grp = df_despesas.groupby('category_name')['amount'].sum().reset_index()

            

            # Group small slices into 'Outros' for the pie chart

            df_desp_grp_pie = df_desp_grp.copy()

            threshold_desp = 0.03 * total_despesas

            mask_desp = df_desp_grp_pie['amount'] < threshold_desp

            if mask_desp.any():

                outros_val = df_desp_grp_pie.loc[mask_desp, 'amount'].sum()

                df_desp_grp_pie = df_desp_grp_pie[~mask_desp]

                df_desp_grp_pie = pd.concat([df_desp_grp_pie, pd.DataFrame([{'category_name': 'Outros', 'amount': outros_val}])], ignore_index=True)

                

            df_desp_grp_pie = df_desp_grp_pie.rename(columns={'category_name': 'Categoria', 'amount': 'Valor'})

    

            df_desp_grp_pie['Categoria_Quebrada'] = df_desp_grp_pie['Categoria'].apply(lambda x: "<br>".join(textwrap.wrap(x, width=30)))
            fig_desp = px.pie(df_desp_grp_pie, values='Valor', names='Categoria_Quebrada', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_desp.update_traces(textposition='inside', textinfo='percent', domain=dict(x=[0, 1], y=[0.3, 1]), hovertemplate="<b>%{label}</b><br>Valor: R$ %{value:,.2f}<br>Participação: %{percent}<extra></extra>")
            fig_desp.update_layout(legend=dict(orientation="h", yanchor="top", y=0.2, xanchor="center", x=0.5), margin=dict(t=20, b=0, l=0, r=0), height=500)
            st.plotly_chart(fig_desp, use_container_width=True)

            

            df_desp_table = df_despesas.groupby('category_name').agg(Quantidade=('id', 'count'), Valor=('amount', 'sum')).reset_index()
            df_desp_table = df_desp_table.sort_values(by='Valor', ascending=False)
            html_t = "<div style='overflow-x:auto;'><table style='width:100%; border-collapse: collapse; text-align: left; font-size: 14px;'>"
            html_t += "<tr style='border-bottom: 2px solid #aaa;'><th style='padding: 8px;'>Categoria</th><th style='padding: 8px; text-align:right;'>Porcentagem</th><th style='padding: 8px; width: 100px;'>Valor</th></tr>"
            for _, row in df_desp_table.iterrows():
                pct = f"{(row['Valor'] / total_despesas * 100):.2f}%"
                val_str = f"{row['Valor']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                html_t += f"<tr style='border-bottom: 1px solid #ddd;'><td style='padding: 8px;'>{row['category_name']}</td><td style='padding: 8px; text-align:right;'>{pct}</td><td style='padding: 8px;'><div style='display: flex; justify-content: space-between; width: 85px; margin-left: auto;'><span>R$</span><span style='white-space: nowrap;'>{val_str}</span></div></td></tr>"
            total_val_str = f"{total_despesas:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            html_t += f"<tr style='font-weight: bold; color: #c0392b; border-top: 2px solid #aaa;'><td style='padding: 8px;'>TOTAL DESPESAS</td><td style='padding: 8px; text-align:right;'>100.00%</td><td style='padding: 8px;'><div style='display: flex; justify-content: space-between; width: 85px; margin-left: auto;'><span>R$</span><span style='white-space: nowrap;'>{total_val_str}</span></div></td></tr>"
            html_t += "</table></div>"
            st.markdown(html_t, unsafe_allow_html=True)

        else:

            st.info("Nenhuma despesa neste período.")

    

    st.markdown("---")

    st.subheader("Glossário das Categorias Utilizadas")

    

    

    

    all_cats_period = df_period['category_name'].unique()

    if len(all_cats_period) > 0:

        glossario_data = []
        for cat in all_cats_period:
            info = GLOSSARIO_INFO.get(cat, {"Tipo": "-", "Descrição": "-"})
            glossario_data.append({
                "Tipo": info["Tipo"],
                "Categoria": cat,
                "Descrição": info.get("Descrição", info.get("Descriǜo", "-"))
            })
        df_glossario = pd.DataFrame(glossario_data)
        
        tipo_order = {"Recebimentos": 1, "Despesas fixas": 2, "Despesas variáveis": 3}
        df_glossario['Tipo_Order'] = df_glossario['Tipo'].map(tipo_order).fillna(4)
        
        df_glossario = df_glossario.sort_values(by=['Tipo_Order', 'Categoria'])
        df_glossario = df_glossario.drop(columns=['Tipo_Order'])
        
        st.table(df_glossario.set_index('Tipo'))

        # Print Button
        st.markdown('<div class="no-print">', unsafe_allow_html=True)
        col_space, col_btn = st.columns([4, 1])
        with col_btn:
            st.components.v1.html("""<button onclick="window.parent.print()" style="float: right; background-color:#2ecc71; color:white; border:none; padding:15px 20px; border-radius:10px; cursor:pointer; font-weight:bold; font-size:16px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);"><span style='font-size:20px;'>🖨️</span> Imprimir</button>""", height=70)
        st.markdown('</div>', unsafe_allow_html=True)

    else:

        st.write("Sem dados para este período.")

    



elif page == "Fluxo de Caixa Gerencial":

    import plotly.graph_objects as go

    

    st.title("📈 Fluxo de Caixa Gerencial")

    st.markdown("Acompanhamento da evolução de receitas, despesas e saldo no tempo.")

    

    if df_transactions.empty:

        st.warning("Sem dados suficientes.")

        st.stop()

        

    df_transactions['period'] = df_transactions['year'].astype(str) + "-" + df_transactions['month'].astype(str).str.zfill(2)

    periods = sorted(df_transactions['period'].unique())

    

    current_year = str(datetime.today().year)

    periods_in_year = [p for p in periods if p.startswith(current_year)]

    if periods_in_year:

        default_start = periods_in_year[0]

        default_end = periods_in_year[-1]

    else:

        default_start = periods[0]

        default_end = periods[-1]

        

        st.sidebar.header("Filtros do Fluxo")
    
    if 'sel_start' not in st.session_state:
        st.session_state.sel_start = default_start
    if 'sel_end' not in st.session_state:
        st.session_state.sel_end = default_end
        
    st.sidebar.markdown("**Filtros Rápidos**")
    col1, col2 = st.sidebar.columns(2)
    col3, col4 = st.sidebar.columns(2)
    
    def set_quick_filter(months_back):
        today = datetime.today()
        if today.month == 1:
            end_m, end_y = 12, today.year - 1
        else:
            end_m, end_y = today.month - 1, today.year
            
        end_q = f"{end_y}-{end_m:02d}"
        
        if months_back is None:
            start_q = periods[0]
            end_q = periods[-1]
        else:
            total_months = end_y * 12 + end_m - 1
            start_total_months = total_months - (months_back - 1)
            start_y = start_total_months // 12
            start_m = start_total_months % 12 + 1
            start_q = f"{start_y}-{start_m:02d}"
            
        valid_starts = [p for p in periods if p >= start_q]
        st.session_state.sel_start = valid_starts[0] if valid_starts else periods[0]
        
        valid_ends = [p for p in periods if p <= end_q]
        st.session_state.sel_end = valid_ends[-1] if valid_ends else periods[-1]

    if col1.button("3 meses", use_container_width=True): set_quick_filter(3)
    if col2.button("6 meses", use_container_width=True): set_quick_filter(6)
    if col3.button("1 ano", use_container_width=True): set_quick_filter(12)
    if col4.button("2 anos", use_container_width=True): set_quick_filter(24)
    if st.sidebar.button("Desde o início", use_container_width=True): set_quick_filter(None)
    
    st.sidebar.markdown("---")
    
    start_period = st.sidebar.selectbox("Mês/Ano Inicial", periods, key='sel_start')
    end_period = st.sidebar.selectbox("Mês/Ano Final", periods, key='sel_end')

    

    df_fc = df_transactions[(df_transactions['period'] >= start_period) & (df_transactions['period'] <= end_period)]

    

    if df_fc.empty:

        st.info("Nenhum dado neste período.")

    else:

        df_hist = df_transactions[df_transactions['period'] < start_period]

        fluxo_hist = df_hist.apply(lambda row: row['amount'] if row['transaction_type'] == 'revenue' else -row['amount'], axis=1).sum()

        saldo_inicial_periodo = SALDO_INICIAL_2023 + fluxo_hist

        

        df_grp = df_fc.groupby('period').apply(

            lambda g: pd.Series({

                'Receitas': g[g['transaction_type'] == 'revenue']['amount'].sum(),

                'Despesas': g[g['transaction_type'].isin(['variable_expense', 'fixed_expense'])]['amount'].sum()

            })

        ).reset_index()

        

        df_grp['Resultado'] = df_grp['Receitas'] - df_grp['Despesas']

        

        saldos = []

        saldo_atual = saldo_inicial_periodo

        for res in df_grp['Resultado']:

            saldo_atual += res

            saldos.append(saldo_atual)

        df_grp['Saldo Acumulado'] = saldos

        

        month_abbr = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

        def format_period(p):

            y, m = p.split('-')

            return f"{month_abbr[int(m)-1]}/{y}"

            

        df_grp['Mês Formatado'] = df_grp['period'].apply(format_period)

        

        fig = go.Figure()

        

        fig.add_trace(go.Scatter(

            x=df_grp['Mês Formatado'], y=df_grp['Saldo Acumulado'],

            name='Saldo Acumulado',

            mode='lines',

            line=dict(color='rgba(52, 152, 219, 1.0)', width=2),

            fill='tozeroy',

            fillcolor='rgba(52, 152, 219, 0.45)',

            hovertemplate="<b>%{x}</b><br>Saldo Acumulado: R$ %{y:,.2f}<extra></extra>"

        ))

        

        fig.add_trace(go.Bar(

            x=df_grp['Mês Formatado'], y=df_grp['Receitas'],

            name='Receitas',

            marker_color='#1dd1a1',

            hovertemplate="<b>%{x}</b><br>Receitas: R$ %{y:,.2f}<extra></extra>"

        ))

        

        fig.add_trace(go.Bar(

            x=df_grp['Mês Formatado'], y=-df_grp['Despesas'],

            customdata=df_grp['Despesas'],

            name='Despesas',

            marker_color='#ff6b6b',

            hovertemplate="<b>%{x}</b><br>Despesas: R$ %{customdata:,.2f}<extra></extra>"

        ))

        

        fig.add_trace(go.Scatter(

            x=df_grp['Mês Formatado'], y=df_grp['Resultado'],

            name='Resultado',

            mode='lines+markers',

            marker_color='#34495e',

            line=dict(width=3),

            hovertemplate="<b>%{x}</b><br>Resultado: R$ %{y:,.2f}<extra></extra>"

        ))

        

        fig.update_layout(
            barmode='relative',
            xaxis_title='',
            yaxis_title='Valores (R$)',
            hovermode='x unified',
            dragmode='pan',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        

        st.plotly_chart(fig, use_container_width=True, config={
            'displayModeBar': True,
            'scrollZoom': False,
            'modeBarButtonsToRemove': ['zoom2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'select2d', 'lasso2d'],
            'displaylogo': False
        })

# Tabela Dinâmica Detalhada

        st.markdown("### Detalhamento Categoria x Mês")

        

        df_fc_copy = df_fc.copy()

        df_fc_copy['Mês Formatado'] = df_fc_copy['period'].apply(format_period)

        

        df_rec_pivot = df_fc_copy[df_fc_copy['transaction_type'] == 'revenue'].pivot_table(index='category_name', columns='Mês Formatado', values='amount', aggfunc='sum').fillna(0)

        df_desp_pivot = df_fc_copy[df_fc_copy['transaction_type'].isin(['variable_expense', 'fixed_expense'])].pivot_table(index='category_name', columns='Mês Formatado', values='amount', aggfunc='sum').fillna(0)

        

        total_rec = df_rec_pivot.sum(axis=0)

        total_desp = df_desp_pivot.sum(axis=0)

        

        ordered_cols = df_grp['Mês Formatado'].tolist()

        

        def format_html_cell(val, prev_val, row_type, is_bold=False):
            color = ''
            if is_bold:
                if row_type == 'REC': color = '#27ae60'
                elif row_type == 'DESP': color = '#c0392b'
                elif row_type in ['RES', 'SAL']:
                    if val > 0: color = '#27ae60'
                    elif val < 0: color = '#c0392b'
                    else: color = 'gray'
            else:
                if row_type in ['RES', 'SAL']:
                    if val > 0: color = '#27ae60'
                    elif val < 0: color = '#c0392b'
                    else: color = 'gray'
            color_style = f"color:{color};" if color else ""
            indicator = ""
            if prev_val is not None:
                if val == 0 and prev_val == 0: indicator = ""
                elif val > prev_val: indicator = " <span style='color:#27ae60; font-weight:bold;'>↑</span>"
                elif val < prev_val: indicator = " <span style='color:#c0392b; font-weight:bold;'>↓</span>"
                else: indicator = " <span style='color:gray; font-weight:bold;'>-</span>"
            val_str = f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            return f"<div style='display: flex; justify-content: space-between; width: 85px; margin-left: auto; {color_style}'><span>R$</span><span style='white-space: nowrap; text-align: right;'>{val_str}{indicator}</span></div>"
            
        def build_row(cat_name, row_series, row_type, is_bold=False, indent=0):
            html = f"<tr style='border-bottom: 1px solid #ddd;'>"
            weight = "bold" if is_bold else "normal"
            padding_left = 8 + (indent * 20)
            html += f"<td style='padding: 8px 8px 8px {padding_left}px; font-weight: {weight};'>{cat_name}</td>"
            prev_val = None
            for col in ordered_cols:
                val = row_series.get(col, 0)
                cell_html = format_html_cell(val, prev_val, row_type, is_bold)
                html += f"<td style='padding: 8px; font-weight: {weight};'>{cell_html}</td>"
                prev_val = val
            html += "</tr>"
            return html
            
        html_table = "<div style='overflow-x:auto;'><table style='width:100%; border-collapse: collapse; text-align: left; font-size: 14px;'>"
        html_table += "<thead><tr style='border-bottom: 2px solid #aaa;'><th style='padding: 8px; position: sticky; top: 0; background-color: #0e1117; z-index: 2;'>Categoria</th>"
        for col in ordered_cols:
            html_table += f"<th style='padding: 8px; position: sticky; top: 0; background-color: #0e1117; z-index: 2;'>{col}</th>"
        html_table += "</tr></thead><tbody>"
        
        html_table += build_row("RECEITAS (TOTAL)", total_rec, "REC", is_bold=True)
        for cat in sorted(df_rec_pivot.index):
            html_table += build_row(cat, df_rec_pivot.loc[cat], "REC", is_bold=False, indent=1)
            
        html_table += "<tr style='border-top: 2px solid #aaa;'></tr>"
        html_table += build_row("DESPESAS (TOTAL)", total_desp, "DESP", is_bold=True)
        for cat in sorted(df_desp_pivot.index):
            html_table += build_row(cat, df_desp_pivot.loc[cat], "DESP", is_bold=False, indent=1)
            
        html_table += "<tr style='border-top: 2px solid #aaa;'></tr>"
        res_series = df_grp.set_index('Mês Formatado')['Resultado']
        html_table += build_row("RESULTADO", res_series, "RES", is_bold=True)
        
        html_table += "<tr style='border-top: 2px solid #aaa;'></tr>"
        saldo_series = df_grp.set_index('Mês Formatado')['Saldo Acumulado']
        html_table += build_row("SALDO ACUMULADO", saldo_series, "SAL", is_bold=True)
        html_table += "</tbody></table></div>"

        

        st.markdown(html_table, unsafe_allow_html=True)


    st.markdown('<div class="pagebreak"></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("Glossário das Categorias")
    
    glossario_data = []
    for cat, info in GLOSSARIO_INFO.items():
        glossario_data.append({
            "Tipo": info["Tipo"],
            "Categoria": cat,
            "Descrição": info["Descrição"]
        })
    df_glossario_completo = pd.DataFrame(glossario_data)
    
    tipo_order = {"Recebimentos": 1, "Despesas fixas": 2, "Despesas variáveis": 3}
    df_glossario_completo['Tipo_Order'] = df_glossario_completo['Tipo'].map(tipo_order).fillna(4)
    
    df_glossario_completo = df_glossario_completo.sort_values(by=['Tipo_Order', 'Categoria'])
    df_glossario_completo = df_glossario_completo.drop(columns=['Tipo_Order'])
    
    st.table(df_glossario_completo.set_index('Tipo'))
