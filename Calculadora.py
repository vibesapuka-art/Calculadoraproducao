
import streamlit as st

# --- Configurações Iniciais da Página ---
st.set_page_config(
    page_title="Calculadora de Lucro Real de Vendas",
    page_icon="💰",
    layout="centered"
)

# --- Título Principal ---
st.title("💰 Calculadora de Lucro Real de Vendas")
st.subheader("Calcule o lucro líquido da sua produção, considerando todos os custos e taxas.")

# --- Seção de Entradas de Valores (Colunas para Organização) ---
st.markdown("---")
st.header("1. Custos de Produção")

col1, col2 = st.columns(2)

with col1:
    custo_material = st.number_input(
        "Custo Total de Materiais (R$)",
        min_value=0.00,
        value=30.00,
        step=0.01,
        format="%.2f",
        help="Soma de todos os custos diretos da produção do item."
    )

with col2:
    custo_mao_obra = st.number_input(
        "Custo com Mão de Obra e Embalagem (R$)",
        min_value=0.00,
        value=15.00,
        step=0.01,
        format="%.2f",
        help="Custos de tempo/serviço e valor da embalagem."
    )

# --- Seção de Venda ---
st.markdown("---")
st.header("2. Preço de Venda")

preco_venda = st.number_input(
    "Preço de Venda ao Cliente (R$)",
    min_value=0.01,
    value=150.00,
    step=0.01,
    format="%.2f",
    help="O valor final cobrado do cliente."
)

# --- Seção de Taxas e Percentuais (Marketplace) ---
st.markdown("---")
st.header("3. Taxas e Impostos")

col3, col4 = st.columns(2)

with col3:
    taxa_marketplace = st.number_input(
        "Taxa do Marketplace (%)",
        min_value=0.0,
        max_value=100.0,
        value=15.0,
        step=0.1,
        format="%.2f",
        help="Percentual cobrado pela plataforma (Ex: Mercado Livre, Etsy, Elo7, etc.)."
    )

with col4:
    taxa_imposto = st.number_input(
        "Impostos/Outras Taxas (%)",
        min_value=0.0,
        max_value=100.0,
        value=6.0,
        step=0.1,
        format="%.2f",
        help="Simples Nacional, taxas bancárias ou outras despesas variáveis."
    )

# --- Função Principal de Cálculo ---
def calcular_lucro_real(venda, material, mao_obra, tx_mp, tx_imposto):
    # 1. Calcular o valor das taxas (em R$)
    valor_taxa_mp = venda * (tx_mp / 100)
    valor_taxa_imposto = venda * (tx_imposto / 100)
    
    # 2. Calcular o Custo Total da Venda
    custo_total_venda = material + mao_obra + valor_taxa_mp + valor_taxa_imposto
    
    # 3. Calcular Lucros
    lucro_bruto = venda - (material + mao_obra)
    lucro_real = venda - custo_total_venda
    
    return custo_total_venda, lucro_bruto, lucro_real, valor_taxa_mp, valor_taxa_imposto

# --- Execução do Cálculo e Exibição dos Resultados ---

custo_total, lucro_bruto, lucro_real, valor_mp, valor_imposto = calcular_lucro_real(
    preco_venda,
    custo_material,
    custo_mao_obra,
    taxa_marketplace,
    taxa_imposto
)

st.markdown("---")
st.header("4. Resultado do Lucro Real")

# Define a cor do lucro
if lucro_real > 0:
    cor = 'green'
    status = "LUCRO POSITIVO 🎉"
elif lucro_real == 0:
    cor = 'orange'
    status = "EMPATE ⚠️"
else:
    cor = 'red'
    status = "PREJUÍZO 😢"

# Exibe o Lucro Real em destaque
st.metric(
    label=f"Lucro Real na Venda ({status})",
    value=f"R$ {lucro_real:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
    delta=f"R$ {lucro_real:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)

# --- Detalhamento dos Custos ---
st.markdown("<br>", unsafe_allow_html=True)
st.subheader("Detalhes Financeiros:")

st.info(
    f"""
    * **Custo Total Fixo de Produção:** R$ {(custo_material + custo_mao_obra):,.2f}
    * **Lucro Bruto (Antes de Taxas):** R$ {lucro_bruto:,.2f}
    * **Taxa do Marketplace ({taxa_marketplace}%):** R$ {valor_mp:,.2f}
    * **Impostos/Outras Taxas ({taxa_imposto}%):** R$ {valor_imposto:,.2f}
    * **Custos Totais da Venda (Todos os gastos):** R$ {custo_total:,.2f}
    """.replace(",", "X").replace(".", ",").replace("X", ".")
)

if lucro_real <= 0:
    st.error(f"⚠️ **Atenção:** Você precisa aumentar o preço de venda ou reduzir os custos em R$ {abs(lucro_real):,.2f} para ter lucro!".replace(",", "X").replace(".", ",").replace("X", "."))

# --- Dicas de Deploy ---
st.sidebar.title("Próximo Passo:")
st.sidebar.info(
    """
    **Para publicar e acessar no navegador:**
    
    1. **Salve este código** como `calculadora_lucro.py`.
    2. **Crie um arquivo** `requirements.txt` na mesma pasta, contendo apenas:
       ```
       streamlit
       ```
    3. **Faça o upload** de ambos os arquivos para um repositório no seu GitHub.
    4. **Acesse o Streamlit Community Cloud** (share.streamlit.io) e faça o deploy do seu repositório.
    """
)
