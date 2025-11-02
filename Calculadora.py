import streamlit as st
import pandas as pd
import io 
import json 
import time

# --- Configurações Iniciais e Session State ---
st.set_page_config(
    page_title="Calculadora de Preço - Lucro Desejado",
    page_icon="💰",
    layout="wide" 
)

# Inicializa o Session State.
if 'insumos_base' not in st.session_state:
    st.session_state.insumos_base = [{'nome': 'Ex: Papel Pacote', 'valor_pacote': 27.50, 'qtd_pacote': 50.0, 'unidade': 'UN'}]

if 'materiais_produto' not in st.session_state:
    st.session_state.materiais_produto = [{'nome': 'Ex: Material A', 'custo_unidade': 0.00, 'qtd_usada': 1.0}]

if 'custos_venda' not in st.session_state or 'custo_fixo_mo_embalagem' not in st.session_state.custos_venda:
    st.session_state.custos_venda = {
        'custo_fixo_mo_embalagem': 0.00,
        'preco_venda': 100.00, # Valor padrão para MOCK
        'taxa_imposto': 0.0, 
        
        # CUSTOS DE MARKETPLACE FLEXÍVEIS
        'taxa_comissao': {'tipo': 'percentual', 'valor': 15.0}, 
        'taxa_por_item': {'tipo': 'fixo', 'valor': 3.00},
        'custo_frete': {'tipo': 'fixo', 'valor': 15.00}
    }

# --- Funções de Manipulação do Session State ---

def adicionar_insumo():
    """Adiciona um novo insumo base (pacote/unidade)"""
    st.session_state.insumos_base.append({'nome': '', 'valor_pacote': 0.00, 'qtd_pacote': 1.0, 'unidade': 'UN'})

def remover_ultimo_insumo():
    """Remove o último insumo base adicionado."""
    if len(st.session_state.insumos_base) > 1:
        st.session_state.insumos_base.pop()
    elif len(st.session_state.insumos_base) == 1:
        st.session_state.insumos_base[0] = {'nome': 'Ex: Papel Pacote', 'valor_pacote': 0.00, 'qtd_pacote': 1.0, 'unidade': 'UN'}

def adicionar_material_produto():
    """Adiciona um item à lista de materiais usados na montagem do produto."""
    st.session_state.materiais_produto.append({'nome': '', 'custo_unidade': 0.00, 'qtd_usada': 1.0})

def remover_ultimo_material_produto():
    """Remove o último item da montagem do produto."""
    if len(st.session_state.materiais_produto) > 1:
        st.session_state.materiais_produto.pop()
    elif len(st.session_state.materiais_produto) == 1:
        st.session_state.materiais_produto[0] = {'nome': 'Ex: Material A', 'custo_unidade': 0.00, 'qtd_usada': 1.0}


# --- Funções de Backup e Restauração ---

def criar_backup_json():
    """Compila os dados importantes do session state em uma string JSON."""
    backup_data = {
        'insumos_base': st.session_state.insumos_base,
        'materiais_produto': st.session_state.materiais_produto,
        'custos_venda': st.session_state.custos_venda
    }
    # Retorna o JSON formatado em string
    return json.dumps(backup_data, indent=4)

def restaurar_estado(uploaded_file):
    """Lê o arquivo JSON e atualiza o session state."""
    if uploaded_file is not None:
        try:
            # Lê o conteúdo do arquivo
            file_content = uploaded_file.getvalue().decode("utf-8")
            data = json.loads(file_content)
            
            # Atualiza o Session State com os dados do arquivo
            st.session_state.insumos_base = data.get('insumos_base', [])
            st.session_state.materiais_produto = data.get('materiais_produto', [])
            st.session_state.custos_venda = data.get('custos_venda', {})
            
            # Confirmação visual antes do rerun
            with st.spinner("Restaurando configurações..."):
                time.sleep(1) 

            st.success("✅ Configurações restauradas com sucesso! Recarregando a aplicação...")
            # Força o reran para atualizar a tela com os novos dados
            st.experimental_rerun()
            
        except json.JSONDecodeError:
            st.error("❌ Erro ao ler o arquivo. Certifique-se de que é um arquivo JSON válido gerado pela calculadora.")
        except Exception as e:
            st.error(f"❌ Ocorreu um erro ao restaurar os dados: {e}")


# --- Função de Cálculo Principal (Direto) ---

def calcular_lucro_real(venda, custo_material_total, custo_fixo_mo_embalagem, tx_imposto, taxas_mp):
    
    def calcular_custo_flexivel(tipo, valor, venda):
        if tipo == 'percentual':
            return venda * (valor / 100)
        return valor
    
    valor_taxa_comissao = calcular_custo_flexivel(
        taxas_mp['taxa_comissao']['tipo'],
        taxas_mp['taxa_comissao']['valor'],
        venda
    )

    valor_taxa_por_item = calcular_custo_flexivel(
        taxas_mp['taxa_por_item']['tipo'],
        taxas_mp['taxa_por_item']['valor'],
        venda
    )

    # CHAVE CORRIGIDA: 'custo_frete'
    valor_custo_frete = calcular_custo_flexivel(
        taxas_mp['custo_frete']['tipo'],
        taxas_mp['custo_frete']['valor'], 
        venda
    )
    
    valor_taxa_imposto = venda * (tx_imposto / 100) 
    custos_marketplace_total = valor_taxa_comissao + valor_taxa_por_item + valor_custo_frete
    custo_producao_base = custo_material_total + custo_fixo_mo_embalagem 
    custo_total_venda = custo_producao_base + custos_marketplace_total + valor_taxa_imposto
    lucro_bruto = venda - custo_producao_base
    lucro_real = venda - custo_total_venda
    
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

# --- Função de Cálculo Reverso (Lucro Fixo Desejado) ---

def calcular_preco_sugerido_lucro_fixo(custo_material_total, custo_fixo_mo_embalagem, tx_imposto, taxas_mp, lucro_fixo_desejado):
    """Calcula o preço de venda ideal baseado em um lucro fixo desejado (R$)."""
    
    # 1. Componentes Percentuais
    comissao_percentual = 0.0
    if taxas_mp['taxa_comissao']['tipo'] == 'percentual':
        comissao_percentual = taxas_mp['taxa_comissao']['valor'] / 100
        
    # 2. Componentes Fixos
    custo_base_producao = custo_material_total + custo_fixo_mo_embalagem
    
    custos_fixos_mp = 0.0
    if taxas_mp['taxa_por_item']['tipo'] == 'fixo':
        custos_fixos_mp += taxas_mp['taxa_por_item']['valor']
    if taxas_mp['custo_frete']['tipo'] == 'fixo':
        custos_fixos_mp += taxas_mp['custo_frete']['valor']
    if taxas_mp['taxa_comissao']['tipo'] == 'fixo':
        custos_fixos_mp += taxas_mp['taxa_comissao']['valor']

    # Numerador: Custo total fixo a ser coberto + Lucro desejado
    numerador = custo_base_producao + custos_fixos_mp + lucro_fixo_desejado
    
    # 3. Denominador (Percentuais que reduzem a receita)
    imposto_percentual = tx_imposto / 100
    
    denominador = 1 - (comissao_percentual + imposto_percentual)
    
    if denominador <= 0:
        return 0.0, 'inválido'
        
    preco_sugerido = numerador / denominador
    
    return preco_sugerido, 'ok'


# --- Função de Formatação (Padrão BRL) ---

def formatar_brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- FUNÇÃO PARA CONVERTER O RESULTADO EM CSV ---
def convert_data_to_csv(data_dict, preco_sugerido, margem_real):
    df_data = {
        'Metrica': [
            'Preco Sugerido (Venda)', 
            'Custo Total da Venda', 
            'Custo de Producao (Base)', 
            'Lucro Real (Desejado)',
            'Margem Real (%)',
            'Custo: Materiais',
            'Custo: Imposto',
            'Custo: Comissao Marketplace',
            'Custo: Taxa por Item + Frete'
        ],
        'Valor': [
            preco_sugerido,
            data_dict['custo_total_sugerido'],
            data_dict['custo_producao_base_sugerido'],
            data_dict['lucro_real_sugerido'],
            margem_real,
            data_dict['custo_material_total'],
            data_dict['valor_imposto_sugerido'],
            data_dict['valor_comissao_sugerida'],
            data_dict['valor_item_sugerido'] + data_dict['valor_frete_sugerido']
        ]
    }
    df = pd.DataFrame(df_data)
    
    # Gera o CSV e codifica em UTF-8
    buffer = io.StringIO()
    # Usando ';' como separador para melhor compatibilidade com Excel em PT-BR
    df.to_csv(buffer, index=False, sep=';', encoding='utf-8') 
    return buffer.getvalue().encode('utf-8')


# --- Título Principal ---

st.title("💰 Calculadora de Preço Ideal por Lucro Desejado")
st.caption("Ajuste os **Materiais** e as **Taxas de Venda** e use a Aba 1 para definir seu Preço.")

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

# 3. CÁLCULO MOCK (Para exibição na Aba 3)
PRECO_MOCK = 100.00

# Execução do cálculo mock (usando o preço de R$ 100 para calcular custos fixos/percentuais para a Aba 3)
(
    _, 
    _, 
    _, 
    _, 
    _, 
    valor_comissao,
    valor_item,
    valor_frete
) = calcular_lucro_real(
    PRECO_MOCK, 
    custo_total_materiais_produto,
    st.session_state.custos_venda['custo_fixo_mo_embalagem'], 
    st.session_state.custos_venda['taxa_imposto'],
    st.session_state.custos_venda
)

# --------------------------------------------------------------------------
# --- DEFINIÇÃO DAS ABAS ---
# --------------------------------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs(["1. Preço Sugerido (Lucro R$)", "2. Materiais & Custos", "3. Taxas de Venda", "4. Backup & Exportação"])


# ==========================================================================
# --- ABA 1: PREÇO SUGERIDO ---
# ==========================================================================
with tab1:
    
    st.header("🎯 Defina o Lucro Desejado em Reais (R$)")
    st.caption("O sistema irá calcular o preço de venda que cobre todos os custos (materiais e taxas) e garante o lucro exato abaixo.")
    
    st.markdown("---")
        
    # Entrada de Lucro Fixo Desejado (R$)
    lucro_fixo_desejado = st.number_input(
        "Qual o **Lucro Fixo** (em R$) você deseja ter por venda?",
        min_value=0.00,
        value=5.00,
        step=0.50,
        format="%.2f",
        key="lucro_fixo_input",
        help="Este é o valor exato que sobrará após todos os custos serem pagos."
    )
    
    # --- Cálculo Reverso ---
    preco_sugerido, status = calcular_preco_sugerido_lucro_fixo(
        custo_total_materiais_produto,
        st.session_state.custos_venda['custo_fixo_mo_embalagem'],
        st.session_state.custos_venda['taxa_imposto'],
        st.session_state.custos_venda,
        lucro_fixo_desejado
    )
    
    if status == 'inválido':
        st.error("⚠️ **Erro de Cálculo:** As taxas de comissão e imposto juntas ultrapassam 100%. Verifique as taxas na Aba 3.")
    else:
        
        st.subheader("2. Preço de Venda Ideal Sugerido")
        
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
        
        margem_real_sugerida = (lucro_real_sugerido / preco_sugerido) * 100 if preco_sugerido > 0 else 0.0

        # Armazenar os resultados no Session State para uso na Aba 4
        resultado_final = {
            'custo_total_sugerido': custo_total_sugerido,
            'lucro_real_sugerido': lucro_real_sugerido,
            'custo_producao_base_sugerido': custo_producao_base_sugerido,
            'valor_imposto_sugerido': valor_imposto_sugerido,
            'valor_comissao_sugerida': valor_comissao_sugerida,
            'valor_item_sugerido': valor_item_sugerido,
            'valor_frete_sugerido': valor_frete_sugerido,
            'custo_material_total': custo_total_materiais_produto
        }
        st.session_state['resultado_final'] = resultado_final
        st.session_state['preco_sugerido'] = preco_sugerido
        st.session_state['margem_real_sugerida'] = margem_real_sugerida
        st.session_state['lucro_fixo_desejado'] = lucro_fixo_desejado

        # --- Exibe o Resultado ---
        
        col_sugerido, col_custo_t, col_lucro_r = st.columns(3)

        with col_sugerido:
            st.metric("Preço Sugerido ao Cliente", formatar_brl(preco_sugerido))
            st.caption(f"Margem Real: {margem_real_sugerida:,.1f}%")

        with col_custo_t:
            st.metric("Custo Total da Venda", formatar_brl(custo_total_sugerido))

        with col_lucro_r:
            st.metric(f"Lucro Real Atingido (Desejado: {formatar_brl(lucro_fixo_desejado)})", formatar_brl(lucro_real_sugerido))
        
        st.success(f"**Recomendação:** Seu lucro real será de **{formatar_brl(lucro_real_sugerido)}** se você vender a **{formatar_brl(preco_sugerido)}**.")
        
        st.markdown("---")
        st.info("Para **Exportação de Dados (CSV/JSON)** ou **Impressão**, acesse a **Aba 4**.")
        
        # --- Detalhamento (Mantido) ---
        st.markdown("##### Detalhamento do Preço Sugerido:")

        col_ds1, col_ds2 = st.columns(2)
        
        with col_ds1:
            st.info(f"""
            **1. Custos de Produção (R$):**
            * Materiais do Produto: {formatar_brl(custo_total_materiais_produto)}
            * Custo Fixo/MO/Embalagem: {formatar_brl(st.session_state.custos_venda['custo_fixo_mo_embalagem'])}
            * **Subtotal Base:** {formatar_brl(custo_producao_base_sugerido)}
            """)
    
        with col_ds2:
            st.info(f"""
            **2. Custos de Venda e Lucro (R$):**
            * Taxa de Comissão (MP): {formatar_brl(valor_comissao_sugerida)}
            * Taxa por Item + Frete: {formatar_brl(valor_item_sugerido + valor_frete_sugerido)}
            * Impostos/Outras Taxas ({st.session_state.custos_venda['taxa_imposto']}%): {formatar_brl(valor_imposto_sugerido)}
            * **Lucro Real Desejado:** {formatar_brl(lucro_fixo_desejado)}
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
    st.subheader("Custo Fixo/MO/Embalagem Adicional")
    st.session_state.custos_venda['custo_fixo_mo_embalagem'] = st.number_input(
        "R$ Custo Fixo por Produto (Ex: Mão de Obra, Embalagem)",
        min_value=0.0,
        value=st.session_state.custos_venda['custo_fixo_mo_embalagem'],
        step=0.10,
        format="%.2f",
        key="custo_fixo_mo_embalagem_input",
        help="Custo que você tem por unidade, que não é material (e.g., R$ 2,50 de tempo/mão de obra, R$ 1,50 de embalagem)."
    )
    
    st.markdown("---")
    st.subheader("Total de Custo com Materiais Usados: " + formatar_brl(custo_total_materiais_produto + st.session_state.custos_venda['custo_fixo_mo_embalagem']))


# ==========================================================================
# --- ABA 3: TAXAS DE VENDA --- 
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
        key="taxa_imposto_input",
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
             # Informa ao usuário que o cálculo é baseado no preço mock
             if key == 'taxa_comissao':
                st.caption(f"Custo Calculado (Base R$ {PRECO_MOCK:,.2f})")

    st.subheader("Custos de Venda (Marketplace)")
    
    st.markdown("##### Taxa de Comissão")
    custo_flexivel_ui('taxa_comissao', 'Comissão (MP)', valor_comissao)
    st.markdown("---")


    st.markdown("##### Taxa por Item Vendido")
    custo_flexivel_ui('taxa_por_item', 'Taxa p/ Item', valor_item)
    st.markdown("---")

    st.markdown("##### Custo de Frete (Pago por Você)")
    custo_flexivel_ui('custo_frete', 'Frete', valor_frete)


# ==========================================================================
# --- ABA 4: BACKUP & EXPORTAÇÃO ---
# ==========================================================================
with tab4:
    
    st.header("💾 Backup, Restauração e Exportação")
    st.caption("Use esta aba para salvar (Exportar) todas as configurações e carregar (Importar) backups existentes.")
    
    st.subheader("1. 📤 Exportar Configurações (Backup)")
    
    st.info("O arquivo de backup salva **todos os materiais, insumos e taxas** configurados nas abas 2 e 3.")
    
    backup_json_string = criar_backup_json()
    
    st.download_button(
        label="⬇️ Baixar Backup de Configurações (.json)",
        data=backup_json_string.encode('utf-8'),
        file_name="calculadora_backup.json",
        mime="application/json",
        use_container_width=True,
        type="primary"
    )
    
    st.markdown("---")
    
    st.subheader("2. 📥 Importar Configurações (Restauração)")
    
    uploaded_file = st.file_uploader(
        "Selecione um arquivo .json de backup gerado pela calculadora.", 
        type="json",
        key="upload_backup"
    )
    
    if uploaded_file is not None:
        st.button("🔄 Restaurar Configurações", on_click=restaurar_estado, args=(uploaded_file,), type="secondary")
        
    st.markdown("---")

    st.subheader("3. 📑 Exportar Resultado Final e Impressão")
    
    # Verifica se o cálculo da Aba 1 foi executado (se as chaves existem)
    if 'resultado_final' in st.session_state and 'preco_sugerido' in st.session_state:
        
        col_csv, col_print = st.columns([1, 2])
        
        with col_csv:
            csv_data = convert_data_to_csv(
                st.session_state.resultado_final,
                st.session_state.preco_sugerido,
                st.session_state.margem_real_sugerida
            )
            st.download_button(
                label="⬇️ Baixar Resumo de Custos (CSV)",
                data=csv_data,
                file_name=f"resumo_preco_{st.session_state.lucro_fixo_desejado:.2f}.csv",
                mime="text/csv",
                use_container_width=True,
                type="secondary"
            )
            st.caption("Salva o cálculo da Aba 1 em formato de planilha.")
            
        with col_print:
            st.markdown("##### Gerar PDF da Tela")
            st.info("""
            Use o atalho **`Ctrl+P`** (ou `Cmd+P` no Mac) do seu navegador. 
            Selecione 'Salvar como PDF' para exportar a tela completa, **incluindo todas as abas abertas**!
            """)
            
    else:
        st.warning("⚠️ O cálculo principal na Aba 1 deve ser executado pelo menos uma vez para gerar os dados de exportação (CSV).")
