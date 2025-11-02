import streamlit as st

# --- Configurações Iniciais e Session State ---
st.set_page_config(
    page_title="Calculadora de Lucro Real de Vendas",
    page_icon="💰",
    layout="centered"
)

# Inicializa o Session State para armazenar a lista de materiais, se ainda não existir
if 'materiais' not in st.session_state:
    # A lista de materiais armazena dicionários: [{'nome': 'Material A', 'custo': 30.00}]
    st.session_state.materiais = [{'nome': 'Ex: Material A', 'custo': 30.00}]

# --- Funções de Manipulação do Session State ---

def adicionar_material():
    """Adiciona um novo item de material com valores padrão."""
    st.session_state.materiais.append({'nome': '', 'custo': 0.00})

def remover_ultimo_material():
    """Remove o último item adicionado, se houver mais de um."""
    if len(st.session_state.materiais) > 1:
        st.session_state.materiais.pop()
    elif len(st.session_state.materiais) == 1:
        # Se houver apenas um, apenas reseta o valor em vez de remover
        st.session_state.materiais[0] = {'nome': 'Ex: Material A', 'custo': 0.00}

# --- Título Principal ---
st.title("💰 Calculadora de Lucro Real de Vendas")
st.subheader("Calcule o lucro líquido da sua produção, considerando todos os custos e taxas.")

# --- Seção de Entradas Dinâmicas de Materiais ---
st.markdown("---")
st.header("1. Custos de Materiais (Adicione seus itens)")

# Botões para adicionar/remover materiais
col_add, col_remove = st.columns([1, 1])
with col_add:
    st.button("➕ Adicionar Material", on_click=adicionar_material, use_container_width=True, type="primary")
with col_remove:
    st.button("➖ Remover Último", on_click=remover_ultimo_material, use_container_width=True, type="secondary")

# Variável para somar o custo total dos materiais
custo_total_materiais = 0.0

# Itera sobre a lista de materiais e cria os campos de entrada
for i, material in enumerate(st.session_state.materiais):
    col_item_nome, col_item_custo = st.columns([2, 1])
    
    with col_item_nome:
        # st.text_input para o nome do material
        material['nome'] = st.text_input(
            f"Nome do Material #{i+1}", 
            value=material['nome'],
            key=f"nome_{i}" # Chave única é obrigatória para widgets dinâmicos
        )

    with col_item_custo:
        # st.number_input para o custo do material
        custo = st.number_input(
            "Custo (R$)", 
            min_value=0.00, 
            value=material['custo'], 
            step=0.01, 
            format="%.2f",
            key=f"custo_{i}", # Chave única é obrigatória
            label_visibility="collapsed" # Oculta o rótulo para ficar mais limpo
        )
        material['custo'] = custo
        custo_total_materiais += custo # Soma o custo para o total

st.markdown("<br>", unsafe_allow_html=True)
st.metric(
    "Custo Total de Materiais", 
    f"R$ {custo_total_materiais:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)
st.markdown("---")

# --- Seção de Custos Fixos (Antiga Mão de Obra e Embalagem) ---
st.header("2. Custos Fixos da Produção")

custo_mao_obra = st.number_input(
    "Custo Fixo (Mão de Obra, Embalagem, etc.) (R$)",
    min_value=0.00,
    value=15.00,
    step=0.01,
    format="%.2f",
    help="Custos de tempo/serviço e valor da embalagem, por unidade."
)

# --- Seção de Venda, Taxas e Impostos (Mantido) ---
st.markdown("---")
st.header("3. Preço de Venda, Taxas e Impostos")

preco_venda = st.number_input(
    "Preço de Venda ao Cliente (R$)",
    min_value=0.01,
    value=150.00,
    step=0.01,
    format="%.2f",
    help="O valor final cobrado do cliente."
)

col3, col4 = st.columns(2)

with col3:
    taxa_marketplace = st.number_input(
        "Taxa do Marketplace (%)",
        min_value=0.0,
        max_value=100.0,
        value=15.0,
        step=0.1,
        format="%.2f",
        help="Percentual cobrado pela plataforma (Ex: Mercado Livre, Elo7, 15%)."
    )

with col4:
    taxa_imposto = st.number_input(
        "Impostos/Outras Taxas (%)",
        min_value=0.0,
        max_value=100.0,
        value=6.0,
        step=0.1,
        format="%.2f",
        help="Simples Nacional, taxas bancárias ou outras despesas variáveis (Ex: 6%)."
    )

# --- Função Principal de Cálculo ---
def calcular_lucro_real(venda, custo_material_total, custo_fixo_total, tx_mp, tx_imposto):
    # 1. Calcular o valor das taxas (em R$)
    valor_taxa_mp = venda * (tx_mp / 100)
    valor_taxa_imposto = venda * (tx_imposto / 100)
    
    # 2. Calcular o Custo Total da Venda
    custo_total_venda = custo_material_total + custo_fixo_total + valor_taxa_mp + valor_taxa_imposto
    
    # 3. Calcular Lucros
    custo_producao_base = custo_material_total + custo_fixo_total
    lucro_bruto = venda - custo_producao_base
    lucro_real = venda - custo_total_venda
    
    return custo_total_venda, lucro_bruto, lucro_real, valor_taxa_mp, valor_taxa_imposto, custo_producao_base

# --- Execução do Cálculo e Exibição dos Resultados ---

custo_total, lucro_bruto, lucro_real, valor_mp, valor_imposto, custo_producao_base = calcular_lucro_real(
    preco_venda,
    custo_total_materiais,
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
    * **Custo Base de Produção (Materiais + Fixos):** R$ {custo_producao_base:,.2f}
    * **Lucro Bruto (Antes de Taxas):** R$ {lucro_bruto:,.2f}
    * **Taxa do Marketplace ({taxa_marketplace}%):** R$ {valor_mp:,.2f}
    * **Impostos/Outras Taxas ({taxa_imposto}%):** R$ {valor_imposto:,.2f}
    * **Custos Totais da Venda (Todos os gastos):** R$ {custo_total:,.2f}
    """.replace(",", "X").replace(".", ",").replace("X", ".")
)

if lucro_real <= 0:
    st.error(f"⚠️ **Atenção:** Você precisa aumentar o preço de venda ou reduzir os custos em R$ {abs(lucro_real):,.2f} para ter lucro!".replace(",", "X").replace(".", ",").replace("X", "."))
