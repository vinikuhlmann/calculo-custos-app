import pandas as pd
import plotly.express as px
import streamlit as st

from pricecalc import calculate_cost

st.set_page_config(layout="wide")

st.title("Simulador do custo do aplicativo")

with st.container(border=True):

    cols = st.columns(4)
    with cols[0]:
        st.markdown("## Usuários")
        initial_user_amount = st.number_input(
            "Quantidade inicial de usuários", min_value=1, value=5
        )
        user_growth_type = st.radio("Tipo de crescimento", ["Absoluto", "Percentual"])
        if user_growth_type == "Absoluto":
            user_growth_rate = st.number_input(
                "Crescimento mensal de usuários", min_value=1, value=5
            )
        elif user_growth_type == "Percentual":
            user_growth_rate = (
                st.number_input(
                    "Crescimento mensal de usuários (%)", min_value=1, value=5
                )
                / 100
            )
        percentage_of_tier2_auth_users = st.number_input(
            "Porcentagem de usuários usando o login do Google",
            min_value=0.0,
            max_value=1.0,
            value=0.1,
        )

    with cols[1]:
        st.markdown("## Inserção de dados")
        initial_companies_per_user = st.number_input(
            "Quantidade inicial de empresas por usuário", min_value=1, value=100
        )
        monthly_new_companies_per_user = st.number_input(
            "Quantidade mensal de novas empresas por usuário", min_value=0, value=30
        )
        targets_per_company = st.number_input(
            "Quantidade média de targets por empresa", min_value=0, value=50
        )
        actions_per_target = st.number_input(
            "Quantidade média de ações por target", min_value=1, value=10
        )
        bytes_per_row = st.number_input(
            "Tamanho dos dados de cada target em bytes", min_value=1, value=220
        )

    with cols[2]:
        st.markdown("## Análise de dados")
        daily_analysis_per_user = st.number_input(
            "Quantidade diária de análises por usuário", min_value=1, value=10
        )
        companies_analyzed_per_user = st.number_input(
            "Quantidade média de empresas por análise", min_value=1, value=30
        )

    with cols[3]:
        st.markdown("## Lucro")
        app_price = st.number_input(
            "Preço do aplicativo por usuário (US$)", min_value=0.0, value=100.0
        )

    months = 36

    costs, users, storage, revenue = zip(
        *calculate_cost(
            initial_user_amount,
            user_growth_rate,
            user_growth_type,
            initial_companies_per_user,
            monthly_new_companies_per_user,
            targets_per_company,
            actions_per_target,
            daily_analysis_per_user,
            companies_analyzed_per_user,
            bytes_per_row,
            percentage_of_tier2_auth_users,
            app_price,
            months,
        )
    )

    cols = st.columns([2, 1, 1])

    costs_df = pd.DataFrame(costs, columns=["Custo"])
    costs_df["Receita"] = revenue
    costs_df["Mês"] = range(1, months + 1)
    costs_df = costs_df.melt(
        id_vars=["Mês"],
        value_vars=["Custo", "Receita"],
        var_name="Tipo",
        value_name="Valor (US$)",
    )

    fig = px.line(
        costs_df,
        x="Mês",
        y="Valor (US$)",
        log_y=True,
        color="Tipo",
        title="Custo mensal do aplicativo",
    )
    cols[0].plotly_chart(fig, use_container_width=True)

    users_df = pd.DataFrame(users, columns=["Usuários"])
    users_df["Mês"] = range(1, months + 1)
    fig = px.line(
        users_df,
        x="Mês",
        y="Usuários",
        title="Quantidade de usuários",
    )
    cols[1].plotly_chart(fig, use_container_width=True)

    storage_df = pd.DataFrame(storage, columns=["Armazenamento (GB)"])
    storage_df["Mês"] = range(1, months + 1)
    fig = px.line(
        storage_df,
        x="Mês",
        y="Armazenamento (GB)",
        title="Quantidade de armazenamento usado",
    )
    cols[2].plotly_chart(fig, use_container_width=True)
