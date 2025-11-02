import streamlit as st
import pandas as pd

# --- Configurações Iniciais e Session State ---
st.set_page_config(
    page_title="Calculadora de Lucro Real - Personalizados",
    page_icon="💰",
    layout="wide" 
)

# Inicializa o Session State para ambos os tipos de entrada
if 'insumos_base' not in st.session_state:
    # Estrutura: [{'nome': 'Papel A4', 'valor_pacote': 27.50, 'qtd_pacote': 50}]
    st.session_state.insumos_base = [{'nome': 'Ex: Papel Pacote', 'valor_pacote': 27.50, 'qtd_pacote': 50}]

if 'materiais_produto' not in st.session_state:
    # CORREÇÃO APLICADA AQUI: qtd_usada inicializada como float (1.0)
    st.session_state.materiais_produto = [{'nome': 'Ex: Material A', 'custo_unidade': 0.00, 'qtd_usada': 1.0}]

# Inicializa o Session State para outros custos/venda (valores padrão)
if 'custos_venda' not in st.session_state:
    st.session_state.custos_venda = {
        'custo_fixo': 15.00,
        'preco_venda': 150.00,
        'taxa_marketplace': 15.0,
        'taxa_imposto': 6.0
    }

# --- Funções de Manipulação do Session State (Insumos Base) ---

def adicionar_insumo():
    """Adiciona um novo insumo base (pacote/unidade)"""
    st.session_state.insumos_base.append({'nome': '', 'valor_pacote': 0.00, 'qtd_pacote': 1})

def remover_ultimo_insumo():
    """Remove o último insumo base adicionado."""
    if len(st.session_state.insumos_base) > 1:
        st.session_state.insumos_base.pop()
    elif len(st.session_state.insumos_base) == 1:
        st.session_state.insumos_base[0] = {'nome': 'Ex: Papel Pacote', 'valor_pacote': 0.00, 'qtd_pacote': 1}

# --- Funções de Manipulação do Session State (Montagem do Produto) ---

def adicionar_material_produto():
    """Adiciona um item à lista de materiais usados na montagem do produto."""
    # CORREÇÃO APLICADA AQUI: novo item com qtd_usada como float (1.0)
    st.session_state.materiais_produto.append({'nome': '', 'custo_unidade': 0.00, 'qtd_usada': 1.0})

def remover_ultimo_material_produto():
    """Remove o último item da montagem do produto."""
    if len(st.session_state.materiais_produto) > 1:
        st.session_state.materiais_produto.pop()
    elif len(st.session_state.materiais_produto) == 1:
        st.session_state.materiais_produto[0] = {'nome': 'Ex: Material A', 'custo_unidade': 0.00, 'qtd_usada': 1.0}

# --- Função de Cálculo Principal ---

def calcular_lucro_real(venda, custo_material_total, custo_fixo_total, tx_mp, tx_imposto):
    valor_taxa_mp = venda * (tx_mp / 100)
    valor_taxa_imposto = venda * (tx_imposto / 100)
    
    custo_total_venda = custo_material_total + custo_fixo_total + valor_taxa_mp + valor_taxa_imposto
    
    custo_producao_base = custo_material_total + custo_fixo_total
    lucro_bruto = venda - custo_producao_base
    lucro_real = venda - custo_total_venda
    
    return custo_total_venda, lucro_bruto, lucro_real, valor_taxa_mp, valor_imposto, custo_producao_base

# --- Função de Formatação (Padrão BRL) ---

def formatar_brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- Título Principal ---

st.title("💰 Calculadora de Lucro Real - Personalizados")
st.caption("Insira os dados nas abas 'Insumos' e 'Marketplace' para ver o 'Resumo'.")

# --------------------------------------------------------------------------
# --- CÁLCULO E PREPARAÇÃO DE DADOS ANTES DAS ABAS ---
# --------------------------------------------------------------------------

# 1. CÁLCULO DE INSUMOS BASE
insumos_unitarios = {}
for insumo in st.session_state.insumos_base:
    custo_unitario = (insumo['valor_pacote'] / insumo['qtd_pacote']) if insumo['qtd_pacote'] > 0 else 0.0
    insumos_unitarios[insumo['nome']] = custo_unitario

# 2. CÁLCULO DO CUSTO TOTAL DE MATERIAIS DO PRODUTO
custo_total_materiais_produto = 0.0
for material in st.session_state.materiais_produto:
    custo_unitario = material.get('custo_unidade', 0.00)
    qtd_usada = material.get('qtd_usada', 0.00)
    custo_total_materiais_produto += custo_unitario * qtd_usada

# 3. CÁLCULO FINAL (usando valores do Session State)
custo_total, lucro_bruto, lucro_real, valor_mp, valor_imposto, custo_producao_base = calcular_lucro_real(
    st.session_state.custos_venda['preco_venda'],
    custo_total_materiais_produto,
    st.session_state.custos_venda['custo_fixo'],
    st.session_state.custos_venda['taxa_marketplace'],
    st.session_state.custos_venda['taxa_imposto']
)

# --------------------------------------------------------------------------
# --- DEFINIÇÃO DAS ABAS ---
# --------------------------------------------------------------------------

tab1, tab2, tab3 = st.tabs(["1. Resumo & Lucro Final", "2. Insumos & Montagem", "3. Marketplace & Outros Custos"])


# ==========================================================================
# --- ABA 1: RESUMO & LUCRO FINAL ---
# ==========================================================================
with tab1:
    st.header("Análise Rápida de Resultado")
    
    # Define a cor e status do lucro
    if lucro_real > 0:
        status = "LUCRO POSITIVO 🎉"
    elif lucro_real == 0:
        status = "EMPATE ⚠️"
    else:
        status = "PREJUÍZO 😢"
    
    col_venda, col_custo, col_lucro = st.columns(3)
    
    with col_venda:
        st.metric("Preço de Venda", formatar_brl(st.session_state.custos_venda['preco_venda']))

    with col_custo:
        st.metric("Custo Total (Todos os Gastos)", formatar_brl(custo_total))

    with col_lucro:
        st.metric(f"Lucro Real por Unidade ({status})", formatar_brl(lucro_real), delta=formatar_brl(lucro_real))

    st.markdown("---")
    st.subheader("Detalhamento dos Custos:")

    # Exibe os detalhes em colunas para organização
    col_d1, col_d2 = st.columns(2)
    
    with col_d1:
        st.info(f"""
        **Custos de Produção (R$):**
        * **Materiais do Produto:** {formatar_brl(custo_total_materiais_produto)}
        * **Custos Fixos/MO/Embalagem:** {formatar_brl(st.session_state.custos_venda['custo_fixo'])}
        * **Custo Base Total:** {formatar_brl(custo_producao_base)}
        """)

    with col_d2:
        st.info(f"""
        **Custos Variáveis (R$):**
        * **Taxa do Marketplace ({st.session_state.custos_venda['taxa_marketplace']}%):** {formatar_brl(valor_mp)}
        * **Impostos/Outras Taxas ({st.session_state.custos_venda['taxa_imposto']}%):** {formatar_brl(valor_imposto)}
        * **Lucro Bruto (Antes de Taxas):** {formatar_brl(lucro_bruto)}
        """)

    if lucro_real <= 0:
        st.error(f"⚠️ **Atenção:** Você precisa aumentar o preço de venda ou reduzir os custos em {formatar_brl(abs(lucro_real))} para ter lucro!")

# ==========================================================================
# --- ABA 2: INSUMOS & MONTAGEM ---
# ==========================================================================
with tab2:
    
    # --- SUB-
