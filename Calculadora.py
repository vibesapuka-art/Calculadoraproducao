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
    # CORREÇÃO DE TIPO (float) aplicada para evitar StreamlitMixedNumericTypesError
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
    # CORREÇÃO DE TIPO (float)
    st.session_state.materiais_produto.append({'nome': '', 'custo_unidade': 0.00, 'qtd_usada': 1.0})

def remover_ultimo_material_produto():
    """Remove o último item da montagem do produto."""
    if len(st.session_state.materiais_produto) > 1:
        st.session_state.materiais_produto.pop()
    elif len(st.session_state.materiais_produto) == 1:
        st.session_state.materiais_produto[0] = {'nome': 'Ex: Material A', 'custo_unidade': 0.00, 'qtd_usada': 1.0}

# --- Função de Cálculo Principal (CORRIGIDA) ---

def calcular_lucro_real(venda, custo_material_total, custo_fixo_total, tx_mp, tx_imposto):
    """Calcula todos os custos e lucros. Garante o retorno de 6 valores."""
    valor_taxa_mp = venda * (tx_mp / 100)
    valor_taxa_imposto = venda * (tx_imposto / 100)
    
    custo_total_venda = custo_material_total + custo_fixo_total + valor_taxa_mp + valor_taxa_imposto
    
    custo_producao_base = custo_material_total + custo_fixo_total
    lucro_bruto = venda - custo_producao_base
    lucro_real = venda - custo_total_venda
    
    # RETORNO COMPLETO DE 6 VARIÁVEIS (CORREÇÃO DO NameError)
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

# 3. CÁLCULO FINAL 
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
    
    # --- SUB-SEÇÃO: CÁLCULO DE INSUMOS BASE (Valor Unitário por Pacote) ---
    st.header("2A. 📦 Custo Unitário de Insumos (Pacotes)")
    st.caption("Defina o custo unitário real de materiais comprados em embalagens.")

    col_i_add, col_i_remove = st.columns([1, 1])
    with col_i_add:
        st.button("➕ Adicionar Insumo (Pacote)", on_click=adicionar_insumo, use_container_width=True, type="primary")
    with col_i_remove:
        st.button("➖ Remover Último Insumo", on_click=remover_ultimo_insumo, use_container_width=True, type="secondary")

    for i, insumo in enumerate(st.session_state.insumos_base):
        col_nome, col_pacote, col_qtd, col_unidade = st.columns([2, 1.5, 1, 1.5])
        
        with col_nome:
            insumo['nome'] = st.text_input(
                "Nome", 
                value=insumo['nome'],
                key=f"insumo_nome_{i}",
                label_visibility="collapsed" if i > 0 else "visible"
            )
        with col_pacote:
            insumo['valor_pacote'] = st.number_input(
                "R$ Pacote", 
                min_value=0.00, 
                value=insumo['valor_pacote'], 
                step=0.01, 
                format="%.2f",
                key=f"insumo_pacote_{i}",
                label_visibility="collapsed" if i > 0 else "visible"
            )
        with col_qtd:
            insumo['qtd_pacote'] = st.number_input(
                "Qtd/Pacote", 
                min_value=1, 
                value=insumo['qtd_pacote'], 
                step=1,
                key=f"insumo_qtd_{i}",
                label_visibility="collapsed" if i > 0 else "visible"
            )

        custo_unitario = insumos_unitarios.get(insumo['nome'], 0.00)
        
        with col_unidade:
            st.markdown(f"R$ **{custo_unitario:,.4f}**")
            if i == 0:
                 st.caption("Custo Unitário")

    st.markdown("---")

    # --- SUB-SEÇÃO: MONTAGEM DO PRODUTO (Uso de Materiais) ---
    st.header("2B. 🏗️ Montagem do Produto por Unidade")
    st.caption("Quais materiais e em qual quantidade são usados para *uma* unidade do seu produto.")
    
    col_m_add, col_m_remove = st.columns([1, 1])
    with col_m_add:
        st.button("➕ Adicionar Material ao Produto", on_click=adicionar_material_produto, use_container_width=True, key="btn_add_prod", type="primary")
    with col_m_remove:
        st.button("➖ Remover Último Material", on_click=remover_ultimo_material_produto, use_container_width=True, key="btn_remove_prod", type="secondary")

    opcoes_insumos = list(insumos_unitarios.keys())
    opcoes_insumos.append("Outro (Manual)")

    for i, material in enumerate(st.session_state.materiais_produto):
        col_nome, col_custo, col_qtd, col_total = st.columns([2, 1.5, 1, 1.5])

        # 1. Campo de Seleção ou Entrada Manual
        with col_nome:
            if insumos_unitarios and len(insumos_unitarios) > 0:
                selecao = st.selectbox(
                    "Material",
                    options=opcoes_insumos,
                    index=opcoes_insumos.index(material['nome']) if material['nome'] in opcoes_insumos else len(opcoes_insumos) - 1,
                    key=f"material_sel_{i}",
                    label_visibility="collapsed" if i > 0 else "visible"
                )
                material['nome'] = selecao
                
                if selecao != "Outro (Manual)":
                    material['custo_unidade'] = insumos_unitarios.get(selecao, 0.00)
                
            else:
                material['nome'] = st.text_input(
                    "Material", 
                    value=material['nome'],
                    key=f"material_nome_{i}",
                    label_visibility="collapsed" if i > 0 else "visible"
                )

        # 2. Campo de Custo Unitário (Editável ou Preenchido)
        with col_custo:
            if material['nome'] == "Outro (Manual)" or not insumos_unitarios or len(insumos_unitarios) == 0:
                custo_unidade = st.number_input(
                    "R$ Unidade",
                    min_value=0.00,
                    value=material['custo_unidade'],
                    step=0.01,
                    format="%.2f",
                    key=f"material_custo_{i}",
                    label_visibility="collapsed" if i > 0 else "visible"
                )
                material['custo_unidade'] = custo_unidade
            else:
                st.markdown(f"R$ **{material['custo_unidade']:,.4f}**")
                if i == 0:
                    st.caption("Custo Unitário")

        # 3. Campo de Quantidade Usada
        with col_qtd:
            material['qtd_usada'] = st.number_input(
                "Qtd Usada",
                min_value=0.01,
                value=material['qtd_usada'],
                step=0.01,
                key=f"material_qtd_{i}",
                label_visibility="collapsed" if i > 0 else "visible"
            )
        
        # 4. Cálculo do Custo Total por Item
        custo_total_item = material['custo_unidade'] * material['qtd_usada']
        
        with col_total:
            st.markdown(f"**R$ {custo_total_item:,.2f}**")
            if i == 0:
                st.caption("Custo Total")

    st.markdown("---")
    st.subheader("Total de Custo com Materiais do Produto: " + formatar_brl(custo_total_materiais_produto))


# ==========================================================================
# --- ABA 3: MARKETPLACE & OUTROS CUSTOS ---
# ==========================================================================
with tab3:
    st.header("3A. Preço de Venda")
    
    st.session_state.custos_venda['preco_venda'] = st.number_input(
        "Preço de Venda ao Cliente (R$)",
        min_value=0.01,
        value=st.session_state.custos_venda['preco_venda'],
        step=0.01,
        format="%.2f",
        help="O valor final cobrado do cliente."
    )
    
    st.markdown("---")
    st.header("3B. Taxas e Custos Variáveis")

    col_mp, col_imposto = st.columns(2)

    with col_mp:
        st.session_state.custos_venda['taxa_marketplace'] = st.number_input(
            "Taxa do Marketplace (%)",
            min_value=0.0,
            max_value=100.0,
            value=st.session_state.custos_venda['taxa_marketplace'],
            step=0.1,
            format="%.2f",
            help="Percentual cobrado pela plataforma (Ex: 15%)."
        )
        st.caption(f"Valor em R$: **{formatar_brl(valor_mp)}**")

    with col_imposto:
        st.session_state.custos_venda['taxa_imposto'] = st.number_input(
            "Impostos/Outras Taxas (%)",
            min_value=0.0,
            max_value=100.0,
            value=st.session_state.custos_venda['taxa_imposto'],
            step=0.1,
            format="%.2f",
            help="Simples Nacional, taxas bancárias, etc. (Ex: 6%)."
        )
        st.caption(f"Valor em R$: **{formatar_brl(valor_imposto)}**")
    
    st.markdown("---")
    st.header("3C. Custos Fixos por Unidade")

    st.session_state.custos_venda['custo_fixo'] = st.number_input(
        "Custo Fixo (Mão de Obra, Embalagem, Frete/Envio) (R$)",
        min_value=0.00,
        value=st.session_state.custos_venda['custo_fixo'],
        step=0.01,
        format="%.2f",
        help="Custos de serviço, valor da embalagem (caixa/plástico) e frete pago por unidade (se houver)."
    )
