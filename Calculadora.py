import streamlit as st
import pandas as pd

# --- Configurações Iniciais e Session State ---
st.set_page_config(
    page_title="Calculadora de Lucro Real - Personalizados",
    page_icon="💰",
    layout="centered"
)

# Inicializa o Session State para ambos os tipos de entrada
if 'insumos_base' not in st.session_state:
    # Estrutura: [{'nome': 'Papel A4', 'valor_pacote': 27.50, 'qtd_pacote': 50}]
    st.session_state.insumos_base = [{'nome': 'Ex: Papel Pacote', 'valor_pacote': 27.50, 'qtd_pacote': 50}]

if 'materiais_produto' not in st.session_state:
    # Materiais usados na montagem do produto (agora com o custo unitário calculado)
    st.session_state.materiais_produto = [{'nome': 'Ex: Material A', 'custo_unidade': 0.00, 'qtd_usada': 1}]

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
    st.session_state.materiais_produto.append({'nome': '', 'custo_unidade': 0.00, 'qtd_usada': 1})

def remover_ultimo_material_produto():
    """Remove o último item da montagem do produto."""
    if len(st.session_state.materiais_produto) > 1:
        st.session_state.materiais_produto.pop()
    elif len(st.session_state.materiais_produto) == 1:
        st.session_state.materiais_produto[0] = {'nome': 'Ex: Material A', 'custo_unidade': 0.00, 'qtd_usada': 1}

# --- Título Principal ---
st.title("💰 Calculadora de Lucro Real - Personalizados")
st.subheader("Calcule o lucro líquido por unidade produzida.")

# --- SEÇÃO 1: CÁLCULO DE INSUMOS BASE (Valor Unitário por Pacote) ---
st.markdown("---")
st.header("1. 📦 Custo Unitário de Insumos por Pacote")
st.caption("Aqui você define o custo real por unidade de materiais que são comprados em embalagens.")

# Botões de Insumos
col_i_add, col_i_remove = st.columns([1, 1])
with col_i_add:
    st.button("➕ Adicionar Insumo (Pacote)", on_click=adicionar_insumo, use_container_width=True, type="primary")
with col_i_remove:
    st.button("➖ Remover Último Insumo", on_click=remover_ultimo_insumo, use_container_width=True, type="secondary")

insumos_df_data = []

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

    # Cálculo do Custo Unitário
    custo_unitario = (insumo['valor_pacote'] / insumo['qtd_pacote']) if insumo['qtd_pacote'] > 0 else 0.0
    
    with col_unidade:
        st.markdown(f"**R$ {custo_unitario:,.4f}**") # Mostra o custo unitário calculado
        if i == 0:
             st.caption("Custo Unitário")
    
    # Armazena para exibição final (opcional)
    insumos_df_data.append({
        'Nome': insumo['nome'],
        'Custo Unitário': custo_unitario
    })

# --- FIM DA SEÇÃO DE INSUMOS BASE ---
st.markdown("---")

# --- SEÇÃO 2: MONTAGEM DO PRODUTO (Usando Custos Unitários) ---
st.header("2. 🏗️ Montagem do Produto (Uso de Materiais)")
st.caption("Defina quais materiais e em qual quantidade são usados para *uma* unidade do seu produto.")

# Botões de Materiais do Produto
col_m_add, col_m_remove = st.columns([1, 1])
with col_m_add:
    st.button("➕ Adicionar Material ao Produto", on_click=adicionar_material_produto, use_container_width=True, key="btn_add_prod", type="primary")
with col_m_remove:
    st.button("➖ Remover Último Material", on_click=remover_ultimo_material_produto, use_container_width=True, key="btn_remove_prod", type="secondary")

custo_total_materiais_produto = 0.0
insumos_unitarios = {item['Nome']: item['Custo Unitário'] for item in insumos_df_data}

# Itera sobre a lista de materiais do produto e cria os campos
for i, material in enumerate(st.session_state.materiais_produto):
    col_nome, col_custo, col_qtd, col_total = st.columns([2, 1.5, 1, 1.5])

    # 1. Campo de Seleção ou Entrada Manual
    with col_nome:
        # Tenta usar um selectbox com base nos insumos base, se houver
        if insumos_unitarios and len(insumos_unitarios) > 0:
            opcoes_insumos = list(insumos_unitarios.keys())
            opcoes_insumos.append("Outro (Manual)")
            
            selecao = st.selectbox(
                "Material",
                options=opcoes_insumos,
                index=opcoes_insumos.index(material['nome']) if material['nome'] in opcoes_insumos else len(opcoes_insumos) - 1,
                key=f"material_sel_{i}",
                label_visibility="collapsed" if i > 0 else "visible"
            )
            material['nome'] = selecao
            
            # Se for selecionado um insumo base, preenche o custo unitário automaticamente
            if selecao != "Outro (Manual)":
                material['custo_unidade'] = insumos_unitarios.get(selecao, 0.00)
            
        else:
            # Se não há insumos base, usa text_input
            material['nome'] = st.text_input(
                "Material", 
                value=material['nome'],
                key=f"material_nome_{i}",
                label_visibility="collapsed" if i > 0 else "visible"
            )

    # 2. Campo de Custo Unitário (Editável ou Preenchido)
    with col_custo:
        # Se for "Outro (Manual)" ou não houver insumos, o usuário insere o valor
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
            # Exibe o custo unitário calculado, mas não permite edição
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
    custo_total_materiais_produto += custo_total_item
    
    with col_total:
        st.markdown(f"**R$ {custo_total_item:,.2f}**")
        if i == 0:
            st.caption("Custo Total")

st.markdown("<br>", unsafe_allow_html=True)
st.metric(
    "Custo Total de Materiais do Produto", 
    f"R$ {custo_total_materiais_produto:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)
st.markdown("---")

# --- SEÇÃO 3: CUSTOS FIXOS, VENDA E RESULTADO ---

# O resto do código é o mesmo da versão anterior, usando 'custo_total_materiais_produto'

st.header("3. 💸 Outros Custos e Venda")

custo_mao_obra = st.number_input(
    "Custo Fixo (Mão de Obra, Embalagem, Frete, etc.) (R$)",
    min_value=0.00,
    value=15.00,
    step=0.01,
    format="%.2f",
    help="Custos fixos de serviço, embalagem ou frete por unidade."
)

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
        help="Percentual cobrado pela plataforma (Ex: 15%)."
    )

with col4:
    taxa_imposto = st.number_input(
        "Impostos/Outras Taxas (%)",
        min_value=0.0,
        max_value=100.0,
        value=6.0,
        step=0.1,
        format="%.2f",
        help="Simples Nacional, taxas bancárias, etc. (Ex: 6%)."
    )

# --- Função Principal de Cálculo ---
def calcular_lucro_real(venda, custo_material_total, custo_fixo_total, tx_mp, tx_imposto):
    valor_taxa_mp = venda * (tx_mp / 100)
    valor_taxa_imposto = venda * (tx_imposto / 100)
    
    custo_total_venda = custo_material_total + custo_fixo_total + valor_taxa_mp + valor_taxa_imposto
    
    custo_producao_base = custo_material_total + custo_fixo_total
    lucro_bruto = venda - custo_producao_base
    lucro_real = venda - custo_total_venda
    
    return custo_total_venda, lucro_bruto, lucro_real, valor_taxa_mp, valor_taxa_imposto, custo_producao_base

# --- Execução do Cálculo e Exibição dos Resultados ---

custo_total, lucro_bruto, lucro_real, valor_mp, valor_imposto, custo_producao_base = calcular_lucro_real(
    preco_venda,
    custo_total_materiais_produto, # AGORA USANDO O CUSTO DA MONTAGEM
    custo_mao_obra,
    taxa_marketplace,
    taxa_imposto
)

st.markdown("---")
st.header("4. ✅ Resultado do Lucro Real")

# Exibição do resultado (formatando para o padrão brasileiro R$,. )
def formatar_brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Define a cor do lucro
if lucro_real > 0:
    status = "LUCRO POSITIVO 🎉"
elif lucro_real == 0:
    status = "EMPATE ⚠️"
else:
    status = "PREJUÍZO 😢"

# Exibe o Lucro Real em destaque
st.metric(
    label=f"Lucro Real na Venda ({status})",
    value=formatar_brl(lucro_real),
    delta=formatar_brl(lucro_real)
)

# --- Detalhamento dos Custos ---
st.markdown("<br>", unsafe_allow_html=True)
st.subheader("Detalhes Financeiros:")

st.info(
    f"""
    * **Custo Base de Produção (Montagem + Fixos):** {formatar_brl(custo_producao_base)}
    * **Lucro Bruto (Antes de Taxas):** {formatar_brl(lucro_bruto)}
    * **Taxa do Marketplace ({taxa_marketplace}%):** {formatar_brl(valor_mp)}
    * **Impostos/Outras Taxas ({taxa_imposto}%):** {formatar_brl(valor_imposto)}
    * **Custos Totais da Venda (Todos os gastos):** {formatar_brl(custo_total)}
    """
)

if lucro_real <= 0:
    st.error(f"⚠️ **Atenção:** Você precisa aumentar o preço de venda ou reduzir os custos em {formatar_brl(abs(lucro_real))} para ter lucro!")

# --- Dicas de Deploy ---
st.sidebar.title("Próximo Passo:")
st.sidebar.info(
    """
    **Para publicar e acessar no navegador:**
    
    1. **Salve este código** como `calculadora_lucro.py`.
    2. **Crie/Atualize** o arquivo `requirements.txt` com:
       ```
       streamlit
       pandas
       ```
    3. **Faça o deploy** no Streamlit Community Cloud.
    """
)
