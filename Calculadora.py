import streamlit as st
import pandas as pd

# --- Configurações Iniciais e Session State ---
st.set_page_config(
    page_title="Calculadora de Lucro Real - Personalizados",
    page_icon="💰",
    layout="wide" 
)

# Inicializa o Session State.
# IMPORTANTE: Os valores de quantidade no pacote (qtd_pacote) devem ser float (X.0) 
# para evitar o erro StreamlitMixedNumericTypesError.
if 'insumos_base' not in st.session_state:
    st.session_state.insumos_base = [{'nome': 'Ex: Papel Pacote', 'valor_pacote': 27.50, 'qtd_pacote': 50.0, 'unidade': 'UN'}]

if 'materiais_produto' not in st.session_state:
    st.session_state.materiais_produto = [{'nome': 'Ex: Material A', 'custo_unidade': 0.00, 'qtd_usada': 1.0}]

# Garante que o Session State use a estrutura mais recente
if 'custos_venda' not in st.session_state or 'custo_fixo_mo_embalagem' not in st.session_state.custos_venda:
    st.session_state.custos_venda = {
        'custo_fixo_mo_embalagem': 0.00, # Valor zerado
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
    # IMPORTANTE: Usar 1.0 (float) para evitar erros de tipo
    st.session_state.insumos_base.append({'nome': '', 'valor_pacote': 0.00, 'qtd_pacote': 1.0, 'unidade': 'UN'})

def remover_ultimo_insumo():
    """Remove o último insumo base adicionado."""
    if len(st.session_state.insumos_base) > 1:
        st.session_state.insumos_base.pop()
    elif len(st.session_state.insumos_base) == 1:
        # IMPORTANTE: Usar 1.0 (float) para evitar erros de tipo
        st.session_state.insumos_base[0] = {'nome': 'Ex: Papel Pacote', 'valor_pacote': 0.00, 'qtd_pacote': 1.0, 'unidade': 'UN'}

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

# --- Função de Cálculo Principal (Direto) ---

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
    
    # Custo Fixo (mo de obra/embalagem/outros)
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
        valor_custo_frete # Corrigido NameError (agora é valor_custo_frete)
    )

# --- Função de Cálculo Reverso (Preço Sugerido) ---

def calcular_preco_sugerido(custo_material_total, tx_imposto, taxas_mp, margem_lucro_desejada):
    """Calcula o preço de venda ideal baseado na margem de lucro desejada."""
    
    # 1. Componentes Percentuais
    comissao_percentual = 0.0
    if taxas_mp['taxa_comissao']['tipo'] == 'percentual':
        comissao_percentual = taxas_mp['taxa_comissao']['valor'] / 100
        
    # 2. Componentes Fixos
    custo_base_fixo = custo_material_total
    
    custos_fixos_mp = 0.0
    # Adiciona Taxa por Item FIXA
    if taxas_mp['taxa_por_item']['tipo'] == 'fixo':
        custos_fixos_mp += taxas_mp['taxa_por_item']['valor']
    # Adiciona Custo de Frete FIXO
    if taxas_mp['custo_frete']['tipo'] == 'fixo':
        custos_fixos_mp += taxas_mp['custo_frete']['valor']
        
    # Adiciona Taxa de Comissão FIXA (temporariamente como custo fixo)
    custo_fixo_comissao = 0.0
    if taxas_mp['taxa_comissao']['tipo'] == 'fixo':
        custo_fixo_comissao = taxas_mp['taxa_comissao']['valor']
    
    custo_fixo_total = custo_base_fixo + custos_fixos_mp + custo_fixo_comissao
    
    # 3. Denominador (Percentuais)
    imposto_percentual = tx_imposto / 100
    margem_desejada_decimal = margem_lucro_desejada / 100
    
    # O preço precisa cobrir a margem de lucro, comissão % e imposto %
    percentual_total_perda_e_lucro = margem_desejada_decimal + comissao_percentual + imposto_percentual
    
    denominador = 1 - percentual_total_perda_e_lucro
    
    if denominador <= 0:
        return 0.0, 'inválido' 
        
    preco_sugerido = custo_fixo_total / denominador
    
    return preco_sugerido, 'ok'


# --- Função de Formatação (Padrão BRL) ---

def formatar_brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- Título Principal ---

st.title("💰 Calculadora de Lucro Real - Personalizados")
st.caption("Insira os dados nas abas 'Materiais' e 'Taxas de Venda' para a análise de preço.")

# --------------------------------------------------------------------------
# --- CÁLCULO E PREPARAÇÃO DE DADOS ANTES DAS ABAS ---
# --------------------------------------------------------------------------

# 1. CÁLCULO DE INSUMOS BASE
insumos_unitarios = {}
for insumo in st.session_state.insumos_base:
    qtd_pacote = insumo.get('qtd_pacote', 1.0) 
    if qtd_pacote > 0:
        custo_unitario = insumo['valor_pacote'] / qtd_pacote
    else:
        custo_unitario = 0.0
        
    insumos_unitarios[insumo['nome']] = custo_unitario

# 2. CÁLCULO DO CUSTO TOTAL DE MATERIAIS DO PRODUTO
custo_total_materiais_produto = 0.0
for material in st.session_state.materiais_produto:
    custo_unitario = material.get('custo_unidade', 0.00)
    qtd_usada = material.get('qtd_usada', 0.00)
    custo_total_materiais_produto += custo_unitario * qtd_usada

# 3. CÁLCULO DIRETO (Para uso no modo "Lucro Atual")
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
# --- ABA 1: RESUMO & LUCRO FINAL (RESTRUTURADA) ---
# ==========================================================================
with tab1:
    
    st.header("Modo de Cálculo")
    
    # Alternador de modo
    modo_calculo = st.radio(
        "Selecione o modo de análise:",
        options=["💰 Calcular Lucro Atual (Preço Fixo)", "🎯 Preço Sugerido (Lucro Desejado)"],
        horizontal=True
    )
    
    st.markdown("---")

    if modo_calculo == "💰 Calcular Lucro Atual (Preço Fixo)":
        
        st.subheader("1. Preço de Venda Definido")
        # Campo de Venda (Cálculo Direto)
        st.session_state.custos_venda['preco_venda'] = st.number_input(
            "Preço de Venda ao Cliente (R$)",
            min_value=0.01,
            value=st.session_state.custos_venda['preco_venda'],
            step=0.01,
            format="%.2f",
            help="O valor final cobrado do cliente."
        )
        
        # --- Exibe o Lucro Atual ---
        st.subheader("2. Análise de Lucro")
        
        preco_analisado = st.session_state.custos_venda['preco_venda']
        margem_real = (lucro_real / preco_analisado) * 100 if preco_analisado > 0 else 0.0
        
        col_venda, col_custo, col_lucro_r = st.columns(3)
        
        with col_venda:
            st.metric("Preço Analisado", formatar_brl(preco_analisado))
    
        with col_custo:
            st.metric("Custo Total (Todos os Gastos)", formatar_brl(custo_total))
    
        with col_lucro_r:
            st.metric(f"Lucro Real (Margem: {margem_real:,.1f}%)", formatar_brl(lucro_real), delta=formatar_brl(lucro_real))

        # --- Detalhamento (Opcional, mas útil) ---
        st.markdown("##### Detalhamento dos Custos:")
        
        col_d1, col_d2 = st.columns(2)
        
        with col_d1:
            st.info(f"""
            **Custos de Produção (R$):**
            * **Materiais do Produto:** {formatar_brl(custo_total_materiais_produto)}
            * **Custo Base Total:** {formatar_brl(custo_producao_base)}
            * **Lucro Bruto (Antes de Taxas):** {formatar_brl(lucro_bruto)}
            """)
    
        with col_d2:
            st.info(f"""
            **Custos de Venda (R$):**
            * **Taxa de Comissão (MP):** {formatar_brl(valor_comissao)}
            * **Taxa por Item + Frete:** {formatar_brl(valor_item + valor_frete)}
            * **Impostos/Outras Taxas ({st.session_state.custos_venda['taxa_imposto']}%):** {formatar_brl(valor_imposto)}
            """)
        
    else: # Modo Cálculo Reverso (Preço Sugerido)
        
        st.subheader("1. Margem de Lucro Desejada")
        
        # Entrada de Lucro Desejado
        margem_desejada = st.slider(
            "Qual a margem de **lucro real** (em %) você deseja ter em cima do preço de venda?",
            min_value=5,
            max_value=70,
            value=25,
            step=1,
            format="%d%%",
            help="Esta é a margem de lucro que sobrará após *todos* os custos (materiais, taxas, impostos) serem pagos."
        )
        
        # --- Cálculo Reverso ---
        preco_sugerido, status = calcular_preco_sugerido(
            custo_total_materiais_produto,
            st.session_state.custos_venda['taxa_imposto'],
            st.session_state.custos_venda,
            margem_desejada
        )
        
        if status == 'inválido':
            st.error("⚠️ **Erro de Cálculo:** A margem de lucro e as taxas de comissão e imposto juntas ultrapassam 100%. Verifique as taxas na Aba 3.")
        else:
            
            st.subheader("2. Preço de Venda Ideal")
            
            # Recalcula o lucro e os custos usando o preço sugerido (para exibição detalhada)
            (
                custo_total_sugerido, 
                lucro_bruto_sugerido, 
                lucro_real_sugerido, 
                valor_imposto_sugerido, 
                custo_producao_base_sugerido,
                valor_comissao_sugerida,
                valor_item_sugerido,
                valor_frete_sugerido
            ) = calcular_lucro_real(
                preco_sugerido,
                custo_total_materiais_produto,
                st.session_state.custos_venda['custo_fixo_mo_embalagem'], 
                st.session_state.custos_venda['taxa_imposto'],
                st.session_state.custos_venda
            )

            # --- Exibe o Resultado ---
            
            col_sugerido, col_custo_b, col_lucro_r = st.columns(3)

            with col_sugerido:
                st.metric("Preço Sugerido ao Cliente", formatar_brl(preco_sugerido))

            with col_custo_b:
                st.metric("Custo Base (Materiais)", formatar_brl(custo_total_materiais_produto))

            with col_lucro_r:
                st.metric(f"Lucro Real Atingido (Desejado: {margem_desejada}%)", formatar_brl(lucro_real_sugerido), delta=formatar_brl(lucro_real_sugerido))
            
            st.success(f"**Recomendação:** Seu lucro real será de aproximadamente **{margem_desejada}%** se você vender a **{formatar_brl(preco_sugerido)}**.")
            
            # --- Detalhamento (Opcional, mas útil) ---
            st.markdown("##### Detalhamento do Preço Sugerido:")

            col_ds1, col_ds2 = st.columns(2)
            
            with col_ds1:
                st.info(f"""
                **1. Custos de Produção (R$):**
                * Materiais do Produto: {formatar_brl(custo_total_materiais_produto)}
                * **Subtotal Base:** {formatar_brl(custo_producao_base_sugerido)}
                """)
        
            with col_ds2:
                st.info(f"""
                **2. Custos de Venda e Lucro (R$):**
                * Taxa de Comissão (MP): {formatar_brl(valor_comissao_sugerida)}
                * Taxa por Item + Frete: {formatar_brl(valor_item_sugerido + valor_frete_sugerido)}
                * Impostos/Outras Taxas ({st.session_state.custos_venda['taxa_imposto']}%): {formatar_brl(valor_imposto_sugerido)}
                * **Lucro Real (Margem {margem_desejada}%):** {formatar_brl(lucro_real_sugerido)}
                """)
            
            st.markdown(f"**Total (Custo Base + Venda + Lucro) = {formatar_brl(preco_sugerido)}**")


# ==========================================================================
# --- ABA 2: MATERIAIS & CUSTOS ---
# ==========================================================================
with tab2:
    
    # --- CUSTO DO MATERIAL (PACOTES) COM SELETOR ML/UN ---
    st.header("Custo do Material (Pacotes e Embalagens)")
    st.caption("Defina o custo unitário (UN) ou por mililitro (ML) dos materiais que você compra.")

    col_i_add, col_i_remove = st.columns([1, 1])
    with col_i_add:
        st.button("➕ Adicionar Material (Pacote)", on_click=adicionar_insumo, use_container_width=True, type="primary")
    with col_i_remove:
        st.button("➖ Remover Último Material", on_click=remover_ultimo_insumo, use_container_width=True, type="secondary")

    for i, insumo in enumerate(st.session_state.insumos_base):
        col_nome, col_pacote, col_qtd, col_unidade_tipo, col_unidade_custo = st.columns([2, 1.5, 1, 1, 1.5])
        
        # 1. Nome do Material
        with col_nome:
            insumo['nome'] = st.text_input(
                "Nome", 
                value=insumo['nome'],
                key=f"insumo_nome_{i}",
                label_visibility="collapsed" if i > 0 else "visible"
            )

        # 2. Valor do Pacote
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

        # 3. Quantidade no Pacote
        with col_qtd:
            # TODOS OS VALORES SÃO FLUTUANTES (1.0)
            insumo['qtd_pacote'] = st.number_input(
                "Qtd/Pacote", 
                min_value=1.0, 
                value=insumo.get('qtd_pacote', 1.0), 
                step=1.0,
                key=f"insumo_qtd_{i}",
                label_visibility="collapsed" if i > 0 else "visible"
            )

        # 4. Seletor de Unidade (UN/ML)
        with col_unidade_tipo:
            if 'unidade' not in insumo:
                insumo['unidade'] = 'UN'
                
            insumo['unidade'] = st.selectbox(
                "Tipo",
                options=['UN', 'ML'],
                index=0 if insumo['unidade'] == 'UN' else 1,
                key=f"insumo_unidade_{i}",
                label_visibility="collapsed" if i > 0 else "visible"
            )
            
        # Cálculo do Custo Unitário/ML
        custo_unitario = insumos_unitarios.get(insumo['nome'], 0.00)
        unidade_label = "R$/UN" if insumo['unidade'] == 'UN' else "R$/ML"
        
        # 5. Custo Unitário Calculado
        with col_unidade_custo:
            st.markdown(f"R$ **{custo_unitario:,.4f}**")
            if i == 0:
                 st.caption(unidade_label)


    st.markdown("---")

    # --- USO DE MATERIAL POR UNIDADE DO PRODUTO ---
    st.header("Uso de Material por Unidade do Produto")
    st.caption("Quais materiais e em qual quantidade (UN ou ML) são usados para *uma* unidade do seu produto.")
    
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
            
            # Ajustar a legenda da quantidade usada com base na unidade do insumo (apenas informativo)
            unidade_tipo_uso = 'UN'
            for insumo in st.session_state.insumos_base:
                if insumo['nome'] == material['nome']:
                    unidade_tipo_uso = insumo['unidade']
                    break


        # 2. Campo de Custo Unitário (Editável ou Preenchido)
        with col_custo:
            if material['nome'] == "Outro (Manual)" or not insumos_unitarios or len(insumos_unitarios) == 0:
                custo_unidade = st.number_input(
                    "R$ Unidade/ML",
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
                    st.caption("Custo Unitário/ML")

        # 3. Campo de Quantidade Usada
        with col_qtd:
            material['qtd_usada'] = st.number_input(
                f"Qtd Usada ({unidade_tipo_uso})", 
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
    st.header("Taxas de Venda (Marketplace, Impostos e Frete)")

    # Impostos (sempre em %)
    st.subheader("Impostos e Outras Taxas (%)")
    st.session_state.custos_venda['taxa_imposto'] = st.number_input(
        "Percentual de Imposto/Taxa Fixa (sobre o preço de venda - Ex: Simples Nacional)",
        min_value=0.0,
        max_value=100.0,
        value=st.session_state.custos_venda['taxa_imposto'],
        step=0.01,
        format="%.2f",
        help="Ex: 4% para Simples Nacional. Esse valor será subtraído do preço final."
    )
    st.markdown("---")


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

    st.subheader("Custos de Venda (Marketplace)")
    
    st.markdown("##### Taxa de Comissão")
    custo_flexivel_ui('taxa_comissao', 'Comissão (MP)', valor_comissao)
    st.markdown("---")


    st.markdown("##### Taxa por Item Vendido")
    custo_flexivel_ui('taxa_por_item', 'Taxa p/ Item', valor_item)
    st.markdown("---")

    st.markdown("##### Custo de Frete (Pago por Você)")
    custo_flexivel_ui('custo_frete', 'Frete', valor_frete)
