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
    st.session_state.insumos_base = [{'nome': 'Ex: Papel Pacote', 'valor_pacote': 27.50, 'qtd_pacote': 50}]

if 'materiais_produto' not in st.session_state:
    st.session_state.materiais_produto = [{'nome': 'Ex: Material A', 'custo_unidade': 0.00, 'qtd_usada': 1.0}]

# CORREÇÃO DO KEYERROR: Garante que o Session State use a nova estrutura
if 'custos_venda' not in st.session_state or 'custo_fixo' in st.session_state.custos_venda:
    st.session_state.custos_venda = {
        'custo_fixo_mo_embalagem': 0.00, # CUSTO FIXO ZERADO (Mão de Obra removida, Embalagem pode ser tratada como custo fixo)
        'preco_venda': 150.00,
        'taxa_imposto': 0.0, 
        
        # CUSTOS DE MARKETPLACE FLEXÍVEIS
        'taxa_comissao': {'tipo': 'percentual', 'valor': 15.0}, 
        'taxa_por_item': {'tipo': 'fixo', 'valor': 3.00},
        'custo_frete': {'tipo': 'fixo', 'valor': 15.00}
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
    st.session_state.materiais_produto.append({'nome': '', 'custo_unidade': 0.00, 'qtd_usada': 1.0})

def remover_ultimo_material_produto():
    """Remove o último item da montagem do produto."""
    if len(st.session_state.materiais_produto) > 1:
        st.session_state.materiais_produto.pop()
    elif len(st.session_state.materiais_produto) == 1:
        st.session_state.materiais_produto[0] = {'nome': 'Ex: Material A', 'custo_unidade': 0.00, 'qtd_usada': 1.0}

# --- Função de Cálculo Principal ---

def calcular_lucro_real(venda, custo_material_total, custo_fixo_mo_embalagem, tx_imposto, taxas_mp):
    
    # Função auxiliar para calcular o custo (Fixo ou Percentual)
    def calcular_custo_flexivel(tipo, valor, venda):
        if tipo == 'percentual':
            return venda * (valor / 100)
        return valor # É um custo fixo
    
    # Taxa de Comissão (Marketplace)
    valor_taxa_comissao = calcular_custo_flexivel(
        taxas_mp['taxa_comissao']['tipo'],
        taxas_mp['taxa_comissao']['valor'],
        venda
    )

    # Taxa por Item Vendido
    valor_taxa_por_item = calcular_custo_flexivel(
        taxas_mp['taxa_por_item']['tipo'],
        taxas_mp['taxa_por_item']['valor'],
        venda
    )

    # Custo de Frete
    valor_custo_frete = calcular_custo_flexivel(
        taxas_mp['custo_frete']['tipo'],
        taxas_mp['custo_frete']['valor'],
        venda
    )
    
    # 2. OUTRAS TAXAS (Imposto)
    valor_taxa_imposto = venda * (tx_imposto / 100) 
    
    # 3. CUSTOS TOTAIS
    custos_marketplace_total = valor_taxa_comissao + valor_taxa_por_item + valor_custo_frete
    
    # Mão de Obra removida: Custo base é apenas materiais e embalagem
    custo_producao_base = custo_material_total + custo_fixo_mo_embalagem 
    
    custo_total_venda = custo_producao_base + custos_marketplace_total + valor_taxa_imposto
    
    # 4. LUCROS
    lucro_bruto = venda - custo_producao_base
    lucro_real = venda - custo_total_venda
    
    # Retorno completo dos valores (8 variáveis)
    return (
        custo_total_venda, 
        lucro_bruto, 
        lucro_real, 
        valor_taxa_imposto, 
        custo_producao_base,
        valor_taxa_comissao,
        valor_taxa_por_item,
        valor_custo_frete
    )

# --- Função de Formatação (Padrão BRL) ---

def formatar_brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- Título Principal ---

st.title("💰 Calculadora de Lucro Real - Personalizados")
st.caption("Insira os dados nas abas 'Materiais' e 'Taxas de Venda' para ver o 'Resumo'.")

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

# 3. CÁLCULO FINAL (Espera 8 retornos)
(
    custo_total, 
    lucro_bruto, 
    lucro_real, 
    valor_imposto, 
    custo_producao_base,
    valor_comissao,
    valor_item,
    valor_frete
) = calcular_lucro_real(
    st.session_state.custos_venda['preco_venda'],
    custo_total_materiais_produto,
    st.session_state.custos_venda['custo_fixo_mo_embalagem'], 
    st.session_state.custos_venda['taxa_imposto'],
    st.session_state.custos_venda
)


# --------------------------------------------------------------------------
# --- DEFINIÇÃO DAS ABAS ---
# --------------------------------------------------------------------------

tab1, tab2, tab3 = st.tabs(["1. Resumo & Lucro Final", "2. Materiais & Custos", "3. Taxas de Venda"])


# ==========================================================================
# --- ABA 1: RESUMO & LUCRO FINAL ---
# ==========================================================================
with tab1:
    st.header("Preço de Venda")
    
    # Campo de Venda
    st.session_state.custos_venda['preco_venda'] = st.number_input(
        "Preço de Venda ao Cliente (R$)",
        min_value=0.01,
        value=st.session_state.custos_venda['preco_venda'],
        step=0.01,
        format="%.2f",
        help="O valor final cobrado do cliente."
    )
    
    st.markdown("---")
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
        * **Custo Fixo de Embalagem:** {formatar_brl(st.session_state.custos_venda['custo_fixo_mo_embalagem'])}
        * **Custo Base Total:** {formatar_brl(custo_producao_base)}
        * **Lucro Bruto (Antes de Taxas):** {formatar_brl(lucro_bruto)}
        """)

    with col_d2:
        st.info(f"""
        **Custos de Venda (R$):**
        * **Taxa de Comissão (Marketplace):** {formatar_brl(valor_comissao)}
        * **Taxa por Item Vendido:** {formatar_brl(valor_item)}
        * **Custo de Frete:** {formatar_brl(valor_frete)}
        * **Impostos/Outras Taxas ({st.session_state.custos_venda['taxa_imposto']}%):** {formatar_brl(valor_imposto)}
        """)

    if lucro_real <= 0:
        st.error(f"⚠️ **Atenção:** Você precisa aumentar o preço de venda ou reduzir os custos em {formatar_brl(abs(lucro_real))} para ter lucro!")

# ==========================================================================
# --- ABA 2: MATERIAIS & CUSTOS (REESTRUTURADA) ---
# ==========================================================================
with tab2:
    
    # --- CUSTO FIXO DE EMBALAGEM (Mão de Obra removida) ---
    st.header("Custo Fixo de Embalagem")
    st.session_state.custos_venda['custo_fixo_mo_embalagem'] = st.number_input(
        "Custo da Embalagem (Caixa/Plástico) por Unidade (R$)",
        min_value=0.00,
        value=st.session_state.custos_venda['custo_fixo_mo_embalagem'],
        step=0.01,
        format="%.2f",
        help="Custo fixo da embalagem utilizada (caixa, plástico bolha, etc.)."
    )
    st.markdown("---")

    # --- CUSTO DO MATERIAL (PACOTES) ---
    st.header("Custo do Material (Pacotes)")
    st.caption("Defina o custo unitário real de materiais comprados em embalagens.")

    col_i_add, col_i_remove = st.columns([1, 1])
    with col_i_add:
        st.button("➕ Adicionar Material (Pacote)", on_click=adicionar_insumo, use_container_width=True, type="primary")
    with col_i_remove:
        st.button("➖ Remover Último Material", on_click=remover_ultimo_insumo, use_container_width=True, type="secondary")

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

    # --- MONTAGEM DO PRODUTO POR UNIDADE ---
    st.header("Uso de Material por Unidade do Produto")
    st.caption("Quais materiais e em qual quantidade são usados para *uma* unidade do seu produto.")
    
    col_m_add, col_m_remove = st.columns([1, 1])
    with col_m_add:
        st.button("➕ Adicionar Material Usado", on_click=adicionar_material_produto, use_container_width=True, key="btn_add_prod", type="primary")
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
    st.subheader("Total de Custo com Materiais Usados: " + formatar_brl(custo_total_materiais_produto))


# ==========================================================================
# --- ABA 3: TAXAS DE VENDA (LIMPA) ---
# ==========================================================================
with tab3:
    st.header("Taxas de Venda (Marketplace e Frete)")

    # --- FUNÇÃO AUXILIAR PARA CRIAR O CAMPO DE CUSTO FLEXÍVEL ---
    def custo_flexivel_ui(key, label, valor_calculado):
        
        c_tipo, c_valor, c_resultado = st.columns([1, 1.5, 1])

        with c_tipo:
            st.session_state.custos_venda[key]['tipo'] = st.radio(
                label="Tipo",
                options=['percentual', 'fixo'],
                format_func=lambda x: "%" if x == 'percentual' else "R$",
                index=0 if st.session_state.custos_venda[key]['tipo'] == 'percentual' else 1,
                key=f"{key}_tipo",
                label_visibility="collapsed"
            )
            st.caption(label)

        is_percent = st.session_state.custos_venda[key]['tipo'] == 'percentual'
        
        with c_valor:
            st.session_state.custos_venda[key]['valor'] = st.number_input(
                label="Valor",
                min_value=0.00,
                max_value=100.0 if is_percent else 100000.0,
                value=st.session_state.custos_venda[key]['valor'],
                step=0.01 if is_percent else 0.10,
                format="%.2f",
                key=f"{key}_valor",
                label_visibility="collapsed"
            )

        with c_resultado:
             st.metric("Custo em R$", formatar_brl(valor_calculado), label_visibility="collapsed")
             if key == 'taxa_comissao':
                st.caption("Custo Calculado")

    # --- Aplicação dos Campos ---
    
    st.markdown("##### Taxa de Comissão (Marketplace)")
    custo_flexivel_ui('taxa_comissao', 'Comissão', valor_comissao)
    st.markdown("---")


    st.markdown("##### Taxa por Item Vendido")
    custo_flexivel_ui('taxa_por_item', 'Taxa p/ Item', valor_item)
    st.markdown("---")

    st.markdown("##### Custo de Frete (Pago por Você)")
    custo_flexivel_ui('custo_frete', 'Frete', valor_frete)
